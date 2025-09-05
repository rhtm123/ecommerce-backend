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

def create_payment(amount, estore=None, redirect_url=""):
    """
    Create payment with PhonePe
    
    Args:
        amount: Payment amount in rupees
        estore: EStore instance (optional)
        redirect_url: Platform-specific redirect URL
    
    Returns:
        tuple: (merchant_order_id, standard_pay_response)
    """
    merchant_order_id = str(uuid4())  # Generate unique order ID
    # print(merchant_order_id);
    amount = amount*100  # In paise (e.g., 100 = 1 INR)
    
    # Use provided redirect_url or generate default one
    if not redirect_url:
        if estore and hasattr(estore, 'website_url'):
            redirect_url = f"{estore.website_url}/payment-success"
        else:
            redirect_url = "https://naigaonmarket.com/payment-success"  # Default fallback

    try:
        standard_pay_request = StandardCheckoutPayRequest.build_request(
            merchant_order_id=merchant_order_id,
            amount=amount,
            redirect_url=redirect_url
        )
        standard_pay_response = client.pay(standard_pay_request)
        print("Payment Creation Response:", json.dumps(standard_pay_response.to_dict(), indent=2))
        print("Checkout URL:", standard_pay_response.redirect_url)
        print("Redirect URL set to:", redirect_url)
        
        # Save the merchant_order_id for later use
        return merchant_order_id, standard_pay_response
    except Exception as e:
        print(f"Error creating payment: {e}")
        raise

def check_payment_status(merchant_order_id):
    """
    Check payment status with PhonePe
    
    Args:
        merchant_order_id: The merchant order ID
    
    Returns:
        dict: Payment status response
    """
    try:
        order_status_response = client.get_order_status(merchant_order_id=merchant_order_id)
        print("Order Status Response:", json.dumps(order_status_response.to_dict(), indent=2))
        print("Order State:", order_status_response.state)
        return order_status_response
    except Exception as e:
        print(f"Error checking order status: {e}")
        raise
