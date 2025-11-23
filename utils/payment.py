from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.env import Env
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from uuid import uuid4
import json

from decouple import config

PHONEPE_CLIENT_ID = config('PHONEPE_CLIENT_ID', default="", cast=str)
PHONEPE_CLIENT_SECRET = config('PHONEPE_CLIENT_SECRET', default="", cast=str)
PHONEPE_CLIENT_VERSION = config('PHONEPE_CLIENT_VERSION', default=1, cast=int)
PHONEPE_ENV = config('PHONEPE_ENV', default="SANDBOX", cast=str)


ENV = Env.PRODUCTION if PHONEPE_ENV == "PRODUCTION" else Env.SANDBOX

client = StandardCheckoutClient.get_instance(
    client_id=PHONEPE_CLIENT_ID,
    client_secret=PHONEPE_CLIENT_SECRET,
    client_version=PHONEPE_CLIENT_VERSION,
    env=ENV
)

def create_payment(amount, estore, redirect_url=""):
    merchant_order_id = str(uuid4())  # Generate unique order ID
    # print(merchant_order_id);
    amount = amount*100  # In paise (e.g., 100 = 1 INR)
    
    # Handle redirect URL - use custom if provided, otherwise use existing logic
    if redirect_url:
        # Use the provided redirect_url (for mobile deep linking)
        ui_redirect_url = redirect_url
        print(f"Using custom redirect URL: {ui_redirect_url}")
    else:
        # Use existing logic for web redirect
        if estore.website[-1] == "/":
            ui_redirect_url = estore.website + "checkout/" + merchant_order_id
        else:
            ui_redirect_url = estore.website + "/checkout/" + merchant_order_id
        print(f"Using default website redirect URL: {ui_redirect_url}")

    try:
        standard_pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=merchant_order_id,
            amount=amount,
            redirect_url=ui_redirect_url
        )
        standard_pay_response = client.pay(standard_pay_request)
        print("Payment Creation Response:", json.dumps(standard_pay_response.to_dict(), indent=2))
        print("Checkout URL:", standard_pay_response.redirect_url)
        # Save the merchant_order_id for later use
        return merchant_order_id, standard_pay_response
    except Exception as e:
        print(f"Error creating payment: {e}")
        raise

def check_payment_status(merchant_order_id):
    """
    Check payment status with PhonePe API with robust error handling
    
    Args:
        merchant_order_id: The merchant order ID
    
    Returns:
        dict: Payment status response or fallback response
    """
    try:
        print(f"Checking payment status for order ID: {merchant_order_id}")
        order_status_response = client.get_order_status(merchant_order_id=merchant_order_id)
        
        # Convert to dict and return
        order_status_dict = order_status_response.to_dict()
        print(f"PhonePe API Response: {json.dumps(order_status_dict, indent=2)}")
        
        return order_status_dict
        
    except Exception as e:
        print(f"Error checking order status: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Handle specific JSON decode errors from PhonePe API
        if "JSONDecodeError" in str(e) or "Expecting value" in str(e):
            print("PhonePe API returned empty/invalid response. This might happen for very new transactions.")
            return {
                "state": "PENDING",
                "message": "Payment status check failed - API returned empty response",
                "error_type": "API_EMPTY_RESPONSE",
                "merchant_order_id": merchant_order_id
            }
        
        # Handle other API errors
        elif "HTTP" in str(e) or "timeout" in str(e).lower():
            print("PhonePe API connection issue")
            return {
                "state": "PENDING", 
                "message": "Payment status check failed - API connection issue",
                "error_type": "API_CONNECTION_ERROR",
                "merchant_order_id": merchant_order_id
            }
            
        # Handle unknown errors
        else:
            print(f"Unknown error type: {e}")
            return {
                "state": "UNKNOWN",
                "message": f"Payment status check failed - {str(e)[:100]}",
                "error_type": "UNKNOWN_ERROR",
                "merchant_order_id": merchant_order_id
            }
