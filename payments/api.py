
from ninja import Router, Query, Schema
from typing import Optional
from django.http import HttpResponse
import logging
import json

router = Router()


from .models import Payment


from django.shortcuts import get_object_or_404

from utils.payment import check_payment_status
from utils.pagination import PaginatedResponseSchema, paginate_queryset

from .schemas import PaymentOutSchema, PaymentCreateSchema
from .models import Payment

from ninja_jwt.authentication import JWTAuth
import hashlib

logging.basicConfig(filename='webhook.log', level=logging.INFO)

from decouple import config


# Webhook credentials (store these securely in settings or environment variables)

WEBHOOK_USERNAME = config('PHONEPE_WEBHOOK_USERNAME', default="", cast=str)
WEBHOOK_PASSWORD = config('PHONEPE_WEBHOOK_PASSWORD', default="", cast=str)

# Define the expected payload schema (optional, for validation)
class PhonePePayload(Schema):
    orderId: str
    state: str
    amount: int
    paymentDetails: Optional[list] = None

class PhonePeWebhookRequest(Schema):
    type: str
    payload: PhonePePayload

# Webhook endpoint
@router.post("/phonepe-webhook/")
def phonepe_webhook(request):
    # Get the Authorization header from PhonePe
    received_auth = request.headers.get("Authorization", "")

    # Compute the expected Authorization value
    expected_auth = hashlib.sha256(f"{WEBHOOK_USERNAME}:{WEBHOOK_PASSWORD}".encode()).hexdigest()

    # Verify authorization
    if received_auth != expected_auth:
        return HttpResponse(
            content=json.dumps({"error": "Invalid authorization"}),
            status=401,
            content_type="application/json"
        )

    # Get raw POST data
    try:
        raw_data = request.body.decode("utf-8")
        data = json.loads(raw_data)
        print(data);
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponse(
            content=json.dumps({"error": "Invalid payload"}),
            status=400,
            content_type="application/json"
        )

    # Log the incoming webhook data
    logging.info(f"{request.headers['Date']} - {raw_data}")

    # Extract payment details
    payment_status = data.get("payload", {}).get("state", "UNKNOWN")
    transaction_id = data.get("payload", {}).get("orderId", "N/A")
    amount = data.get("payload", {}).get("amount", 0) / 100  # Convert paise to rupees

    # Notify customer based on payment status
    from .utils import notify_customer
    if payment_status == "COMPLETED":
        message = f"Payment of ₹{amount} for Transaction ID {transaction_id} was successful!"
        notify_customer(message)
    elif payment_status == "FAILED":
        message = f"Payment for Transaction ID {transaction_id} failed. Please try again."
        notify_customer(message)
    else:
        message = f"Payment for Transaction ID {transaction_id} is still processing."
        notify_customer(message)

    # Respond to PhonePe to acknowledge receipt
    return {"success": True, "message": "Webhook received"}




@router.post("/payments/", response=PaymentOutSchema,auth=JWTAuth())
def create_payment(request, payload: PaymentCreateSchema):
    payment = Payment(**payload.dict())
    payment.save()
    return payment

@router.get("/payments/", response=PaginatedResponseSchema)
def payments(request,  
              page: int = Query(1), 
              page_size: int = Query(10), 
              status:str = None ,
              ordering: str = None,):
    
    qs = Payment.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""


    if status:
        qs = qs.filter(status=status)
        query = query + "&status=" + str(status)


    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + str(ordering)


    return paginate_queryset(request, qs, PaymentOutSchema, page_number, page_size, query)


@router.get("/verify-payment", response=PaymentOutSchema)
def verify_payment(request, transaction_id: str = None,):
    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    if payment.payment_method == "pg":
        order_status_response =  check_payment_status(merchant_order_id=transaction_id)
        status = order_status_response['state'].lower()

        if payment.status != status:
            order = payment.order
            order.status = status  # Update the order status to match the payment status
            order.save()  # Save the updated order
            payment.status = status
            payment.save()
    
    return payment