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

# logging.basicConfig(filename='webhook.log', level=logging.INFO)

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

# Additional schema for mobile payment callback
class PaymentWebhookCallbackSchema(Schema):
    """Schema for payment callback from mobile apps"""
    transaction_id: str
    status: str
    amount: Optional[float] = None
    order_id: Optional[int] = None
    platform: Optional[str] = None

# Enhanced webhook endpoint with platform support
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
        print("Webhook data:", data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponse(
            content=json.dumps({"error": "Invalid payload"}),
            status=400,
            content_type="application/json"
        )

    # Extract payment details
    payment_status = data.get("payload", {}).get("state", "UNKNOWN")
    transaction_id = data.get("payload", {}).get("orderId", "N/A")
    amount = data.get("payload", {}).get("amount", 0) / 100  # Convert paise to rupees

    # Find and update payment record
    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
        payment.status = payment_status.lower()
        payment.save()
        
        # Handle platform-specific notifications
        notify_result = notify_customer_by_platform(payment, payment_status, amount)
        
        return {"success": True, "message": "Webhook received", "notification_sent": notify_result}
    except Payment.DoesNotExist:
        # Fallback to original notification system if payment not found
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

        return {"success": True, "message": "Webhook received"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"success": False, "message": "Error processing webhook"}

def notify_customer_by_platform(payment, payment_status, amount):
    """
    Send platform-specific notifications to customers
    """
    try:
        from .utils import notify_customer  # Your existing notification function
        
        if payment_status == "COMPLETED":
            message = f"Payment of ₹{amount} for Transaction ID {payment.transaction_id} was successful!"
            
            if hasattr(payment, 'platform') and payment.platform == 'mobile':
                # For mobile apps, you might want to send push notifications
                send_mobile_notification(payment, message, 'success')
            else:
                # For web, use existing notification method
                notify_customer(message)
                
        elif payment_status == "FAILED":
            message = f"Payment for Transaction ID {payment.transaction_id} failed. Please try again."
            
            if hasattr(payment, 'platform') and payment.platform == 'mobile':
                send_mobile_notification(payment, message, 'failed')
            else:
                notify_customer(message)
        else:
            message = f"Payment for Transaction ID {payment.transaction_id} is still processing."
            
            if hasattr(payment, 'platform') and payment.platform == 'mobile':
                send_mobile_notification(payment, message, 'pending')
            else:
                notify_customer(message)
        
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False

def send_mobile_notification(payment, message, status):
    """
    Send push notification to mobile app
    You can implement this using Firebase FCM or other push notification services
    """
    try:
        # Example implementation - you can integrate with Firebase FCM later
        print(f"Mobile notification for order {payment.order.id}: {message}")
        
        # Here you would integrate with your push notification service
        # notification_data = {
        #     'title': 'Payment Status Update',
        #     'body': message,
        #     'data': {
        #         'type': 'payment_status',
        #         'transaction_id': payment.transaction_id,
        #         'order_id': str(payment.order.id),
        #         'status': status
        #     }
        # }
        
        return True
    except Exception as e:
        print(f"Error sending mobile notification: {e}")
        return False

@router.post("/payments/", response=PaymentOutSchema, auth=JWTAuth())
def create_payment(request, payload: PaymentCreateSchema):
    """
    Enhanced payment creation with platform support
    Defaults to 'web' platform for backward compatibility
    """
    payment_data = payload.dict()
    
    # BACKWARD COMPATIBILITY: Default to web platform
    if not payment_data.get('platform'):
        payment_data['platform'] = 'web'  # Default to web for existing frontend
        
        # Only try to detect mobile if explicitly needed
        user_agent = request.headers.get('User-Agent', '').lower()
        if 'react-native' in user_agent or payment_data.get('device_info'):
            # Only set to mobile if it's clearly a React Native app
            payment_data['platform'] = 'mobile'
    
    # Remove device_info if None to avoid issues with existing code
    if not payment_data.get('device_info'):
        payment_data.pop('device_info', None)
    
    # Log platform information for debugging (only if not web to reduce logs)
    if payment_data.get('platform') != 'web':
        print(f"Creating payment for platform: {payment_data.get('platform')}")
        if payment_data.get('device_info'):
            print(f"Device info: {payment_data['device_info']}")
    
    payment = Payment(**payment_data)
    payment.save()
    return payment

@router.get("/payments/", response=PaginatedResponseSchema)
def payments(request,  
              page: int = 1, 
              page_size: int = 10, 
              status: str = None,
              platform: str = None,  # Added platform filter
              ordering: str = None):
    
    qs = Payment.objects.all()
    query = ""

    if status:
        qs = qs.filter(status=status)
        query = query + "&status=" + str(status)
    
    # NEW: Filter by platform if the field exists
    if platform and hasattr(Payment, 'platform'):
        qs = qs.filter(platform=platform)
        query = query + "&platform=" + str(platform)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + str(ordering)

    return paginate_queryset(request, qs, PaymentOutSchema, page, page_size, query)

@router.get("/verify-payment", response=PaymentOutSchema)
def verify_payment(request, transaction_id: str = None):
    """
    Verify payment status with enhanced error handling
    """
    payment = get_object_or_404(Payment, transaction_id=transaction_id)
    print(f"Verifying payment: {payment.id} with transaction_id: {transaction_id}")

    if payment.payment_method == "pg":
        try:
            order_status_response = check_payment_status(merchant_order_id=transaction_id)
            print(f"Payment verification response: {order_status_response}")
            
            # Check if we got an error response from the utility function
            if 'error_type' in order_status_response:
                print(f"PhonePe API error detected: {order_status_response['error_type']}")
                
                # For API errors, keep the current status but log the issue
                if order_status_response['error_type'] in ['API_EMPTY_RESPONSE', 'API_CONNECTION_ERROR']:
                    print(f"Keeping current payment status '{payment.status}' due to API issues")
                    return payment
                elif order_status_response['error_type'] == 'UNKNOWN_ERROR':
                    print(f"Unknown error occurred, keeping current status: {order_status_response.get('message', '')}")
                    return payment
            
            # Normal response - update payment status
            status = order_status_response.get('state', 'pending').lower()
            print(f"Payment status from PhonePe: {status}, Current status: {payment.status}")
            
            if payment.status != status:
                old_status = payment.status
                payment.status = status
                payment.save()
                print(f"Payment status updated from '{old_status}' to '{status}'")
                
                # Send platform-specific notification if status changed
                if status in ['completed', 'failed']:
                    notify_customer_by_platform(payment, status.upper(), float(payment.amount))
            else:
                print("Payment status unchanged")
                
        except Exception as e:
            print(f"Unexpected error in verify_payment: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Don't fail the request, just log and return current payment state
            print(f"Returning current payment status due to verification error: {payment.status}")
            return payment
    
    return payment

# NEW: Mobile-specific payment callback endpoint
@router.post("/payment-callback/mobile/")
def mobile_payment_callback(request, payload: PaymentWebhookCallbackSchema):
    """
    Handle payment callback specifically for mobile apps
    This endpoint can be called by the mobile app when it receives deep link callbacks
    """
    try:
        payment = Payment.objects.get(transaction_id=payload.transaction_id)
        
        # Verify the payment status with PhonePe
        if payment.payment_method == "pg":
            order_status_response = check_payment_status(merchant_order_id=payload.transaction_id)
            print(order_status_response);
            # Handle API errors gracefully
            if 'error_type' in order_status_response:
                print(f"PhonePe API error in mobile callback: {order_status_response['error_type']}")
                return {
                    "success": False,
                    "status": payment.status,
                    "message": f"Payment verification failed: {order_status_response.get('message', 'API error')}",
                    "error_type": order_status_response['error_type'],
                    "payment": {
                        "id": payment.id,
                        "transaction_id": payment.transaction_id,
                        "status": payment.status,
                        "amount": float(payment.amount),
                        "order_id": payment.order.id
                    }
                }
            
            verified_status = order_status_response.get('state', payment.status).lower()
            
            # Update payment status if it has changed
            if payment.status != verified_status:
                payment.status = verified_status
                payment.save()
                
                return {
                    "success": True,
                    "status": verified_status,
                    "message": "Payment status updated successfully",
                    "payment": {
                        "id": payment.id,
                        "transaction_id": payment.transaction_id,
                        "status": payment.status,
                        "amount": float(payment.amount),
                        "order_id": payment.order.id
                    }
                }
            else:
                return {
                    "success": True,
                    "status": payment.status,
                    "message": "Payment status already up to date",
                    "payment": {
                        "id": payment.id,
                        "transaction_id": payment.transaction_id,
                        "status": payment.status,
                        "amount": float(payment.amount),
                        "order_id": payment.order.id
                    }
                }
        else:
            return {"success": False, "message": "Payment method not supported"}
            
    except Payment.DoesNotExist:
        return {"success": False, "message": "Payment not found"}
    except Exception as e:
        print(f"Error in mobile payment callback: {e}")
        return {"success": False, "message": "Error processing payment callback"}

# NEW: Get platform-specific payment statistics (optional)
@router.get("/payment-stats/")
def payment_stats(request):
    """
    Get payment statistics by platform (if platform field exists)
    """
    try:
        from django.db.models import Count, Sum
        
        if hasattr(Payment, 'platform'):
            stats = Payment.objects.values('platform', 'status').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
        else:
            # Fallback if platform field doesn't exist yet
            stats = Payment.objects.values('status').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
        
        return {"success": True, "data": list(stats)}
    except Exception as e:
        return {"success": False, "message": f"Error fetching stats: {e}"}
