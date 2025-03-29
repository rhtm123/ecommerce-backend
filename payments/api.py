
from ninja import Router, Query

import logging

router = Router()

from pydantic import BaseModel

from .models import Payment

class CreatePaymentPayload(BaseModel):
    amount: int
    mobile: str

class VerifyPaymentPayload(BaseModel):
    order_id: str

logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404

from utils.payment import check_payment_status

from utils.pagination import PaginatedResponseSchema, paginate_queryset

from .schemas import PaymentOutSchema, PaymentCreateSchema
from .models import Payment

from ninja_jwt.authentication import JWTAuth


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
            payment.status = status
            payment.save()
    
    return payment