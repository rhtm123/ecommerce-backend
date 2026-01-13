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
    "https://api.phonepe.com/apis/pg"
    if PHONEPE_ENV == "PRODUCTION"
    else "https://api-preprod.phonepe.com/apis/pg-sandbox"
)

# Cashfree Configuration
CASHFREE_CLIENT_ID = config('CASHFREE_CLIENT_ID', default="", cast=str)
CASHFREE_CLIENT_SECRET = config('CASHFREE_CLIENT_SECRET', default="", cast=str)
CASHFREE_ENV = config('CASHFREE_ENV', default="SANDBOX", cast=str)
CASHFREE_API_VERSION = config('CASHFREE_API_VERSION', default="2025-01-01", cast=str)

# Cashfree API Base URLs
CASHFREE_BASE_URL = (
    "https://api.cashfree.com/pg"
    if CASHFREE_ENV == "PRODUCTION"
    else "https://sandbox.cashfree.com/pg"
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
        
        print(f"Auth token: {auth_data}")
        return access_token
    except Exception as e:
        print(f"Error getting auth token: {e}")
        raise


def create_payment_phonepay(amount, redirect_url, merchant_order_id=None):
    """
    Create payment with PhonePe
    
    Args:
        amount: Payment amount in rupees
        redirect_url: Redirect URL to redirect user after payment (required)
        merchant_order_id: Optional merchant order ID. If not provided, a UUID will be generated.
    
    Returns:
        dict: Payment response with redirectUrl and orderId
    """
    if merchant_order_id is None:
        merchant_order_id = str(uuid4())  # Generate unique order ID if not provided
    amount_in_paise = int(amount * 100)  # Convert to paise (e.g., 100 = 1 INR)
    
    # print(f"Using redirect URL: {redirect_url}")
    
    try:
        # Get authentication token
        auth_token = _get_auth_token()

        # print(auth_token)
        
        # Prepare API request
        url = f"{PHONEPE_BASE_URL}/checkout/v2/pay"
        
        payload = {
            "amount": amount_in_paise,
            "merchantOrderId": merchant_order_id,
            "paymentFlow": {
                "type": "PG_CHECKOUT",
                "merchantUrls": {
                    "redirectUrl": redirect_url
                },
                "paymentModeConfig": {
                    "enabledPaymentModes": [
                        {
                            "type": "UPI_INTENT"
                        },
                        {
                            "type": "UPI_COLLECT"
                        },
                        {
                            "type": "UPI_QR"
                        },
                        {
                            "type": "NET_BANKING"
                        },
                        {
                            "type": "CARD",
                            "cardTypes": [
                                "DEBIT_CARD",
                                "CREDIT_CARD"
                            ]
                        }
                    ],
                    "disabledPaymentModes": [
                        {
                            "type": "UPI_INTENT"
                        },
                        {
                            "type": "UPI_COLLECT"
                        },
                        {
                            "type": "UPI_QR"
                        },
                        {
                            "type": "NET_BANKING"
                        },
                        {
                            "type": "CARD",
                            "cardTypes": [
                                "DEBIT_CARD",
                                "CREDIT_CARD"
                            ]
                        }
                    ]
                }
            },
            "metaInfo":{

            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"O-Bearer {auth_token}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"Payment response: {response.json()}")

        # Check if response is successful
        if response.status_code != 200:
            print(f"PhonePe API returned non-200 status: {response.status_code}")
            raise Exception(f"Payment creation failed with HTTP {response.status_code}")
        
        response_data = response.json()
        
        # PhonePe API wraps the actual payment response in a 'data' field
        # Extract the nested data if it exists, otherwise use the response as is
        if 'data' in response_data and response_data['data']:
            payment_response = response_data['data']
        else:
            payment_response = response_data
        
        # Save the merchant_order_id for later use
        return payment_response
        
    except Exception as e:
        print(f"Error creating PhonePe payment: {e}")
        raise


def create_payment_cashfree(amount, redirect_url, merchant_order_id=None, customer_details=None, link_purpose="Payment"):
    """
    Create payment link with Cashfree
    
    Args:
        amount: Payment amount in rupees
        redirect_url: Return URL to redirect user after payment (required)
        merchant_order_id: Optional link ID. If not provided, a UUID will be generated.
        customer_details: Optional dict with customer_name, customer_email, customer_phone
        link_purpose: Purpose description for the payment link
    
    Returns:
        dict: Payment response with link_url and cf_link_id
    """

    try:
        # Prepare API request
        url = f"{CASHFREE_BASE_URL}/links"
        
        # Default customer details if not provided
        if customer_details is None:
            customer_details = {
                "customer_name": "Customer",
                "customer_email": "testemail@gmail.com",
                "customer_phone": "9999999999"
            }
        
        # Build notify_url (webhook URL) - same domain as return_url
        notify_url = redirect_url.replace("/checkout/", "/api/payment/cashfree-webhook/")
        if not notify_url.startswith("http"):
            # If redirect_url is relative, construct full URL
            base_url = redirect_url.split("/checkout/")[0] if "/checkout/" in redirect_url else "https://nm.thelearningsetu.com"
            notify_url = f"{base_url}/api/payment/cashfree-webhook/"
        
        payload = {
            "link_id": merchant_order_id,
            "link_amount": float(amount),
            "link_currency": "INR",
            "link_purpose": link_purpose,
            "customer_details": customer_details,
            "link_meta": {
                "notify_url": notify_url,
                "return_url": redirect_url,
                "upi_intent": False
            },
            "link_notify": {
                "send_email": False,
                "send_sms": False
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-version": CASHFREE_API_VERSION,
            "x-client-id": CASHFREE_CLIENT_ID,
            "x-client-secret": CASHFREE_CLIENT_SECRET
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"Cashfree payment response: {response.status_code}, {response.text}")
        
        # Check if response is successful
        if response.status_code != 200:
            print(f"Cashfree API returned non-200 status: {response.status_code}")
            raise Exception(f"Cashfree payment creation failed with HTTP {response.status_code}: {response.text}")
        
        response_data = response.json()
        
        # Cashfree returns the response directly, no nesting
        return {
            "redirectUrl": response_data.get("link_url"),
            "link_url": response_data.get("link_url"),
            "orderId": response_data.get("cf_link_id"),  # Cashfree's link ID
            "cf_link_id": response_data.get("cf_link_id"),
            "link_id": response_data.get("link_id"),
            "link_status": response_data.get("link_status")
        }
        
    except Exception as e:
        print(f"Error creating Cashfree payment: {e}")
        raise


def create_payment(amount, redirect_url, merchant_order_id=None, gateway="PhonePe", customer_details=None, link_purpose="Payment"):
    """
    Create payment with specified gateway (PhonePe or Cashfree)
    
    Args:
        amount: Payment amount in rupees
        redirect_url: Redirect/Return URL to redirect user after payment (required)
        merchant_order_id: Optional merchant order/link ID
        gateway: Payment gateway to use ("PhonePe" or "Cashfree"), defaults to "PhonePe"
        customer_details: Optional dict for Cashfree with customer_name, customer_email, customer_phone
        link_purpose: Purpose description for Cashfree payment link
    
    Returns:
        dict: Payment response with redirectUrl/link_url and orderId/cf_link_id
    """
    gateway = gateway.strip() if gateway else "PhonePe"
    
    if gateway.lower() == "cashfree":
        return create_payment_cashfree(amount, redirect_url, merchant_order_id, customer_details, link_purpose)
    else:
        # Default to PhonePe for backward compatibility
        return create_payment_phonepay(amount, redirect_url, merchant_order_id)


def check_payment_status_cashfree(link_id):
    """
    Check payment status with Cashfree API
    
    Args:
        link_id: The Cashfree link_id (cf_link_id) or our link_id
    
    Returns:
        dict: Payment status response
    """
    try:
        # Use Cashfree's Get Payment Link Details endpoint
        url = f"{CASHFREE_BASE_URL}/links/{link_id}"
        
        headers = {
            "x-api-version": CASHFREE_API_VERSION,
            "x-client-id": CASHFREE_CLIENT_ID,
            "x-client-secret": CASHFREE_CLIENT_SECRET
        }
        
        response = requests.get(url, headers=headers)
        print(f"Cashfree status check response: {response.status_code}")
        
        if response.status_code == 404:
            return {
                "state": "PENDING",
                "message": "Payment link not found or still processing",
                "error_type": "API_NOT_FOUND",
                "link_id": link_id
            }
        
        if response.status_code != 200:
            return {
                "state": "PENDING",
                "message": f"Payment status check failed - HTTP {response.status_code}",
                "error_type": "API_HTTP_ERROR",
                "link_id": link_id
            }
        
        response_data = response.json()
        
        # Map Cashfree status to our payment status format
        link_status = response_data.get("link_status", "PENDING")
        link_amount_paid = response_data.get("link_amount_paid", 0)
        link_amount = response_data.get("link_amount", 0)
        
        # Determine state based on Cashfree status and payment amount
        if link_status == "PAID" or (link_amount_paid > 0 and link_amount_paid >= link_amount):
            state = "SUCCESS"
        elif link_status == "EXPIRED" or link_status == "CANCELLED":
            state = "FAILED"
        elif link_status == "PARTIALLY_PAID":
            state = "PENDING"  # Or handle as partial payment
        else:
            state = "PENDING"
        
        return {
            "state": state,
            "link_status": link_status,
            "link_amount": link_amount,
            "link_amount_paid": link_amount_paid,
            "cf_link_id": response_data.get("cf_link_id"),
            "link_id": response_data.get("link_id")
        }
        
    except Exception as e:
        print(f"Error checking Cashfree payment status: {e}")
        return {
            "state": "PENDING",
            "message": f"Payment status check failed - {str(e)[:100]}",
            "error_type": "UNKNOWN_ERROR",
            "link_id": link_id
        }


def check_payment_status_phonepe(merchant_order_id):
    """
    Check payment status with PhonePe API
    
    Args:
        merchant_order_id: The merchant order ID
    
    Returns:
        dict: Payment status response or fallback response
    """
    try:
        # print(f"Checking payment status for order ID: {merchant_order_id}")
        
        # Get authentication token
        auth_token = _get_auth_token()
        
        # Prepare API request
        url = f"{PHONEPE_BASE_URL}/checkout/v2/order/{merchant_order_id}/status"
        
        headers = {
            # "Content-Type": "application/json",
            "Authorization": f"O-Bearer {auth_token}"
        }
        
        response = requests.get(url, headers=headers)
        # print(f"HTTP Response Status Code: {response.status_code}")
        
        # Handle HTTP 204 (No Content) - valid success response but no body
        if response.status_code == 204:
            # print("PhonePe API returned 204 No Content - payment may still be processing")
            return {
                "state": "PENDING",
                "message": "Payment status unavailable - order may still be processing",
                "error_type": "API_NO_CONTENT",
                "merchant_order_id": merchant_order_id
            }
        
        # Check if response is successful (200-299 range)
        if not (200 <= response.status_code < 300):
            # print(f"PhonePe API returned error status: {response.status_code}")
            return {
                "state": "PENDING",
                "message": f"Payment status check failed - HTTP {response.status_code}",
                "error_type": "API_HTTP_ERROR",
                "merchant_order_id": merchant_order_id
            }
        
        # Try to parse JSON response
        try:
            order_status_response = response.json()
        except (json.JSONDecodeError, ValueError) as e:
            # If response is empty or not valid JSON, treat as no content
            print(f"PhonePe API returned non-JSON response: {e}")
            return {
                "state": "PENDING",
                "message": "Payment status unavailable - invalid response format",
                "error_type": "API_INVALID_RESPONSE",
                "merchant_order_id": merchant_order_id
            }
        
        # print(f"PhonePe API Response: {json.dumps(order_status_response, indent=2)}")
        
        # PhonePe API wraps the actual order status in a 'data' field
        # Extract the nested data if it exists
        if 'data' in order_status_response and order_status_response['data']:
            # Return the nested data which contains the actual order status
            return order_status_response['data']
        elif 'state' in order_status_response:
            # If state is directly in the response, return as is (backward compatibility)
            return order_status_response
        else:
            # If neither structure is found, return error
            # print("Unexpected PhonePe API response structure")
            return {
                "state": "PENDING",
                "message": "Payment status check failed - Unexpected API response structure",
                "error_type": "API_INVALID_RESPONSE",
                "merchant_order_id": merchant_order_id,
                "raw_response": order_status_response
            }
        
    except Exception as e:
        # print(f"Error checking order status: {e}")
        # print(f"Error type: {type(e).__name__}")
        
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


def check_payment_status(merchant_order_id, gateway="PhonePe"):
    """
    Check payment status with specified gateway (PhonePe or Cashfree)
    
    Args:
        merchant_order_id: The merchant order ID (for PhonePe) or link_id (for Cashfree)
        gateway: Payment gateway to use ("PhonePe" or "Cashfree"), defaults to "PhonePe"
    
    Returns:
        dict: Payment status response or fallback response
    """
    gateway = gateway.strip() if gateway else "PhonePe"
    
    if gateway.lower() == "cashfree":
        return check_payment_status_cashfree(merchant_order_id)
    
    # Default to PhonePe for backward compatibility
    return check_payment_status_phonepe(merchant_order_id)
