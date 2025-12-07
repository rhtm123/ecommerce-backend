import requests
import json
from uuid import uuid4
from decouple import config

# PhonePe Configuration
PHONEPE_CLIENT_ID = config('PHONEPE_CLIENT_ID', default="", cast=str)
PHONEPE_CLIENT_SECRET = config('PHONEPE_CLIENT_SECRET', default="", cast=str)
PHONEPE_CLIENT_VERSION = config('PHONEPE_CLIENT_VERSION', default=1, cast=int)
PHONEPE_ENV = config('PHONEPE_ENV', default="SANDBOX", cast=str)

# API Base URLs
PHONEPE_BASE_URL = (
    "https://api.phonepe.com/apis"
    if PHONEPE_ENV == "PRODUCTION"
    else "https://api-preprod.phonepe.com/apis/pg-sandbox"
)

# Token cache for authentication
_auth_token_cache = {
    "access_token": None,
    "expires_at": 0
}


def _get_auth_token():
    """
    Get authentication token from PhonePe API.
    Caches the token and reuses it until expiry.
    
    Returns:
        str: Access token for API authentication
    """
    import time
    
    # Check if cached token is still valid
    current_time = time.time()
    if _auth_token_cache["access_token"] and _auth_token_cache["expires_at"] > current_time:
        return _auth_token_cache["access_token"]
    
    # Get new token
    if PHONEPE_ENV == "PRODUCTION":
        url = "https://api.phonepe.com/apis/identity-manager/v1/oauth/token"
    else:
        url = "https://api-preprod.phonepe.com/apis/pg-sandbox/v1/oauth/token"
    
    payload = {
        "client_id": PHONEPE_CLIENT_ID,
        "client_secret": PHONEPE_CLIENT_SECRET,
        "client_version": PHONEPE_CLIENT_VERSION,
        "grant_type": "client_credentials"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        
        auth_data = response.json()
        access_token = auth_data.get("access_token")
        expires_at = auth_data.get("expires_at", 0)
        
        # Cache the token
        _auth_token_cache["access_token"] = access_token
        _auth_token_cache["expires_at"] = expires_at
        
        return access_token
    except Exception as e:
        print(f"Error getting auth token: {e}")
        raise


def create_payment(amount, estore, redirect_url=""):
    """
    Create payment with PhonePe
    
    Args:
        amount: Payment amount in rupees
        estore: EStore instance
        redirect_url: Custom redirect URL (optional, defaults to estore website)
    
    Returns:
        tuple: (merchant_order_id, standard_pay_response)
        
    The standard_pay_response is a mock object with:
        - redirect_url: URL to redirect user for payment
        - to_dict(): method to convert response to dictionary
    """
    merchant_order_id = str(uuid4())  # Generate unique order ID
    amount_in_paise = int(amount * 100)  # Convert to paise (e.g., 100 = 1 INR)
    
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
        # Get authentication token
        auth_token = _get_auth_token()

        print(auth_token)
        
        # Prepare API request
        url = f"{PHONEPE_BASE_URL}/checkout/v2/pay"
        
        payload = {
            "amount": amount_in_paise,
            "merchantOrderId": merchant_order_id,
            "paymentFlow": {
                "type": "PG_CHECKOUT",
                "merchantUrls": {
                    "redirectUrl": ui_redirect_url
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"O-Bearer {auth_token}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        # response.raise_for_status()
        
        response_data = response.json()
        print("Payment Creation Response:", json.dumps(response_data, indent=2))
        
        # Save the merchant_order_id for later use
        return merchant_order_id, response_data
        
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
        
        # Get authentication token
        auth_token = _get_auth_token()
        
        # Prepare API request
        url = f"{PHONEPE_BASE_URL}/checkout/v2/order/{merchant_order_id}/status"
        
        headers = {
            # "Content-Type": "application/json",
            "Authorization": f"O-Bearer {auth_token}"
        }
        
        response = requests.get(url, headers=headers)
        print(f"HTTP Response Status Code: {response}")
        # response.raise_for_status()
        
        order_status_response = response.json()
        
        print(f"PhonePe API Response: {json.dumps(order_status_response, indent=2)}")
        
        return order_status_response
        
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
