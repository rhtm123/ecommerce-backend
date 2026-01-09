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

def map_phonepay_status(phonepay_status):
    """
    Map PhonePe payment status to our payment model status values
    
    PhonePe typically returns: PAYMENT_SUCCESS, PAYMENT_PENDING, PAYMENT_ERROR, etc.
    We need to map these to: completed, pending, failed
    
    Args:
        phonepay_status: Status string from PhonePe API (case-insensitive)
    
    Returns:
        str: Mapped status value ('completed', 'pending', 'failed', 'refunded')
    """
    if not phonepay_status:
        return 'pending'
    
    status_lower = str(phonepay_status).lower()
    
    # Map various PhonePe status values to our payment statuses
    if 'success' in status_lower or 'completed' in status_lower:
        return 'completed'
    elif 'pending' in status_lower or 'processing' in status_lower:
        return 'pending'
    elif 'fail' in status_lower or 'error' in status_lower:
        return 'failed'
    elif 'refund' in status_lower:
        return 'refunded'
    else:
        # Default to pending for unknown statuses
        print(f"Unknown PhonePe status: {phonepay_status}, defaulting to 'pending'")
        return 'pending'

def map_cashfree_status(cashfree_status):
    """
    Map Cashfree payment status to our payment model status values
    
    Args:
        cashfree_status: Status string from Cashfree API
    
    Returns:
        str: Mapped status value ('completed', 'pending', 'failed', 'refunded')
    """
    if not cashfree_status:
        return 'pending'
    
    status_lower = str(cashfree_status).lower()
    
    # Map Cashfree payment status values to our payment statuses
    # Cashfree returns: SUCCESS, PENDING, FAILED, etc.
    if status_lower == 'success' or status_lower == 'paid':
        return 'completed'
    elif status_lower == 'pending' or status_lower == 'active' or 'partially' in status_lower:
        return 'pending'
    elif status_lower == 'failed' or status_lower == 'expired' or status_lower == 'cancelled' or status_lower == 'user_dropped':
        return 'failed'
    elif status_lower == 'refunded' or 'refund' in status_lower:
        return 'refunded'
    else:
        print(f"Unknown Cashfree status: {cashfree_status}, defaulting to 'pending'")
        return 'pending'

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
    order_id = data.get("payload", {}).get("orderId", None)  # PhonePe's Merchant Reference ID
    
    if not order_id:
        return HttpResponse(
            content=json.dumps({"error": "Missing orderId in payload"}),
            status=400,
            content_type="application/json"
        )

    # Find and update payment record
    try:
        # Find payment by transaction_id (which stores the gateway-specific ID)
        payment = Payment.objects.get(transaction_id=order_id)
        
        # Update payment status
        mapped_status = map_phonepay_status(payment_status)
        if payment.status != mapped_status:
            payment.status = mapped_status
            payment.save()
            print(f"Payment {payment.id} status updated to: {mapped_status}")
        else:
            print(f"Payment {payment.id} status unchanged: {mapped_status}")
        
        return {"success": True, "message": "Webhook received and processed"}
        
    except Payment.DoesNotExist:
        print(f"Payment not found for orderId: {order_id}")
        return HttpResponse(
            content=json.dumps({"error": "Payment not found"}),
            status=404,
            content_type="application/json"
        )
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return HttpResponse(
            content=json.dumps({"error": "Error processing webhook"}),
            status=500,
            content_type="application/json"
        )

# Cashfree webhook endpoint
@router.post("/cashfree-webhook/")
def cashfree_webhook(request):
    """
    Handle Cashfree payment webhook
    Cashfree sends webhook notifications when payment status changes
    """
    try:
        # Get raw POST data
        raw_data = request.body.decode("utf-8")
        data = json.loads(raw_data)
        print("Cashfree webhook data:", json.dumps(data, indent=2))
        
        # Cashfree webhook structure:
        # {
        #   "data": {
        #     "order": {
        #       "order_tags": {
        #         "link_id": "e9fa3014-f82c-4aa9-bbc3-f0897215c159"
        #       }
        #     },
        #     "payment": {
        #       "payment_status": "SUCCESS"
        #     }
        #   }
        # }
        webhook_data = data.get("data", {})
        order_data = webhook_data.get("order", {})
        payment_data = webhook_data.get("payment", {})
        
        # Extract link_id from order_tags.link_id (this is what we stored in transaction_id)
        order_tags = order_data.get("order_tags", {})
        link_id = order_tags.get("link_id")
        
        # Extract payment status from payment.payment_status (e.g., "SUCCESS", "FAILED", "PENDING")
        payment_status = payment_data.get("payment_status", "")
        
        if not link_id:
            print(f"Warning: link_id not found in webhook. order_tags: {order_tags}")
            return HttpResponse(
                content=json.dumps({"error": "Missing link_id in webhook payload"}),
                status=400,
                content_type="application/json"
            )
        
        # Find payment record
        try:
            # Find payment by transaction_id (which stores the link_id)
            payment = Payment.objects.get(transaction_id=link_id)
            
            # Map Cashfree payment status to our payment status
            if payment_status:
                mapped_status = map_cashfree_status(payment_status)
                if payment.status != mapped_status:
                    old_status = payment.status
                    payment.status = mapped_status
                    payment.save()
                    print(f"Payment {payment.id} status updated from '{old_status}' to '{mapped_status}' (from Cashfree: {payment_status})")
                else:
                    print(f"Payment {payment.id} status unchanged: {mapped_status}")
            else:
                print(f"Warning: No payment_status in Cashfree webhook for link_id: {link_id}")
            
            return {"success": True, "message": "Cashfree webhook received and processed"}
            
        except Payment.DoesNotExist:
            print(f"Payment not found for Cashfree link_id: {link_id}")
            return HttpResponse(
                content=json.dumps({"error": "Payment not found"}),
                status=404,
                content_type="application/json"
            )
            
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"JSON decode error: {e}")
        return HttpResponse(
            content=json.dumps({"error": "Invalid webhook payload"}),
            status=400,
            content_type="application/json"
        )
    except Exception as e:
        print(f"Error processing Cashfree webhook: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(
            content=json.dumps({"error": "Error processing webhook"}),
            status=500,
            content_type="application/json"
        )

# def notify_customer_by_platform(payment, payment_status, amount):
#     """
#     Send platform-specific notifications to customers
#     """
#     try:
#         from .utils import notify_customer  # Your existing notification function
        
#         if payment_status == "COMPLETED":
#             message = f"Payment of ₹{amount} for Transaction ID {payment.transaction_id} was successful!"
            
#             if hasattr(payment, 'platform') and payment.platform == 'mobile':
#                 # For mobile apps, you might want to send push notifications
#                 send_mobile_notification(payment, message, 'success')
#             else:
#                 # For web, use existing notification method
#                 notify_customer(message)
                
#         elif payment_status == "FAILED":
#             message = f"Payment for Transaction ID {payment.transaction_id} failed. Please try again."
            
#             if hasattr(payment, 'platform') and payment.platform == 'mobile':
#                 send_mobile_notification(payment, message, 'failed')
#             else:
#                 notify_customer(message)
#         else:
#             message = f"Payment for Transaction ID {payment.transaction_id} is still processing."
            
#             if hasattr(payment, 'platform') and payment.platform == 'mobile':
#                 send_mobile_notification(payment, message, 'pending')
#             else:
#                 notify_customer(message)
        
#         return True
#     except Exception as e:
#         print(f"Error sending notification: {e}")
#         return False

# def send_mobile_notification(payment, message, status):
#     """
#     Send push notification to mobile app
#     You can implement this using Firebase FCM or other push notification services
#     """
#     try:
#         # Example implementation - you can integrate with Firebase FCM later
#         print(f"Mobile notification for order {payment.order.id}: {message}")
        
#         # Here you would integrate with your push notification service
#         # notification_data = {
#         #     'title': 'Payment Status Update',
#         #     'body': message,
#         #     'data': {
#         #         'type': 'payment_status',
#         #         'transaction_id': payment.transaction_id,
#         #         'order_id': str(payment.order.id),
#         #         'status': status
#         #     }
#         # }
        
#         return True
#     except Exception as e:
#         print(f"Error sending mobile notification: {e}")
#         return False

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
            # Determine which gateway and ID to use for status check
            gateway = payment.payment_gateway or "PhonePe"
            
            # Use transaction_id for status checks (stores gateway-specific ID)
            status_check_id = payment.transaction_id
            if not status_check_id:
                print(f"Warning: transaction_id not found for payment {payment.id}")
                return payment
            
            print(f"Using {gateway} with transaction_id: {status_check_id}")
            
            order_status_response = check_payment_status(merchant_order_id=status_check_id, gateway=gateway)
            print(f"Payment verification response: {order_status_response}")
            
            # Check if we got an error response from the utility function
            if 'error_type' in order_status_response:
                print(f"{gateway} API error detected: {order_status_response['error_type']}")
                
                # For API errors, keep the current status but log the issue
                if order_status_response['error_type'] in ['API_EMPTY_RESPONSE', 'API_CONNECTION_ERROR', 'API_NO_CONTENT', 'API_INVALID_RESPONSE', 'API_NOT_FOUND']:
                    print(f"Keeping current payment status '{payment.status}' due to API issues: {order_status_response.get('message', '')}")
                    return payment
                elif order_status_response['error_type'] == 'UNKNOWN_ERROR':
                    print(f"Unknown error occurred, keeping current status: {order_status_response.get('message', '')}")
                    return payment
                elif order_status_response['error_type'] == 'API_HTTP_ERROR':
                    # For HTTP errors (4xx, 5xx), also keep current status
                    print(f"HTTP error from {gateway} API, keeping current status: {order_status_response.get('message', '')}")
                    return payment
            
            # Normal response - update payment status based on gateway
            gateway = payment.payment_gateway or "PhonePe"
            
            if gateway.lower() == "cashfree":
                # Cashfree returns link_status in the response
                cashfree_status = order_status_response.get('link_status') or order_status_response.get('state', 'pending')
                status = map_cashfree_status(cashfree_status)
                print(f"Payment status from Cashfree: {cashfree_status} -> mapped to: {status}, Current status: {payment.status}")
            else:
                # PhonePe returns state in the response
                phonepay_status = order_status_response.get('state', 'pending')
                status = map_phonepay_status(phonepay_status)
                print(f"Payment status from PhonePe: {phonepay_status} -> mapped to: {status}, Current status: {payment.status}")
            
            if payment.status != status:
                old_status = payment.status
                payment.status = status
                payment.save()
                print(f"Payment status updated from '{old_status}' to '{status}'")
                
                # Notification functionality commented out
                # if status in ['completed', 'failed']:
                #     notify_customer_by_platform(payment, status.upper(), float(payment.amount))
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
        
        # Verify the payment status with the appropriate gateway
        if payment.payment_method == "pg":
            gateway = payment.payment_gateway or "PhonePe"
            
            # Use transaction_id for status checks (stores gateway-specific ID)
            status_check_id = payment.transaction_id
            if not status_check_id:
                print(f"Warning: transaction_id not found for payment {payment.id}")
                return {
                    "success": False,
                    "status": payment.status,
                    "message": "Transaction ID not found",
                    "payment": {
                        "id": payment.id,
                        "transaction_id": payment.transaction_id,
                        "status": payment.status,
                        "amount": float(payment.amount),
                        "order_id": payment.order.id
                    }
                }
            
            print(f"Using {gateway} with transaction_id: {status_check_id}")
            
            order_status_response = check_payment_status(merchant_order_id=status_check_id, gateway=gateway)
            print(order_status_response);
            # Handle API errors gracefully
            if 'error_type' in order_status_response:
                print(f"{gateway} API error in mobile callback: {order_status_response['error_type']}")
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
            
            # Map status based on gateway
            if gateway.lower() == "cashfree":
                cashfree_status = order_status_response.get('link_status') or order_status_response.get('state', payment.status)
                verified_status = map_cashfree_status(cashfree_status)
            else:
                phonepay_status = order_status_response.get('state', payment.status)
                verified_status = map_phonepay_status(phonepay_status)
            
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
