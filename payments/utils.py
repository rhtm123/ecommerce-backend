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
    """
    Create payment with PhonePe
    
    Args:
        amount: Payment amount in rupees
        estore: EStore instance
        redirect_url: Custom redirect URL (optional, defaults to estore website)
    
    Returns:
        tuple: (merchant_order_id, standard_pay_response)
    """
    merchant_order_id = str(uuid4())  # Generate unique order ID
    amount = amount * 100  # In paise (e.g., 100 = 1 INR)
    
    # BACKWARD COMPATIBILITY: Use custom redirect_url if provided, otherwise use existing logic
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
    Check payment status with PhonePe
    
    Args:
        merchant_order_id: The merchant order ID
    
    Returns:
        dict: Payment status response
    """
    try:
        order_status_response = client.get_order_status(merchant_order_id=merchant_order_id)

        order_status_response = json.dumps(order_status_response.to_dict(), indent=2)
        order_status_response = json.loads(order_status_response)

        return order_status_response

        # order_status_response = json.dumps(order_status_response.to_dict(), indent=2)
        # print("Order State:", order_status_response.state)
        # print(order_status_response, json.dumps(order_status_response.payment_details))
        # return order_status_response, json.dumps(order_status_response.payment_details)
    except Exception as e:
        print(f"Error checking order status: {e}")
        raise
