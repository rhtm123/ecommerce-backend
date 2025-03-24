
from django.conf import settings
from ninja import Router

from uuid import uuid4

from django.conf import settings

from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.env import Env
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest


env = Env.SANDBOX  # Change to Env.PRODUCTION when you go live

import logging

client = None

def create_client():
    global client
    client = StandardCheckoutClient.get_instance(client_id=settings.PHONEPE_CLIENT_ID,
                                                              client_secret=settings.PHONEPE_CLIENT_SECRET,
                                                              client_version=settings.PHONEPE_CLIENT_VERSION,
                                                              env=env)
    

router = Router()

from pydantic import BaseModel

class CreatePaymentPayload(BaseModel):
    amount: int
    mobile: str

class VerifyPaymentPayload(BaseModel):
    order_id: str


@router.post("/create-payment")
def create_payment(request, payload: CreatePaymentPayload):
    """Initiate a PhonePe Payment"""
    if not client:
        create_client()
    unique_order_id = str(uuid4())
    ui_redirect_url = "https://www.merchant.com/redirect"
    standard_pay_request = StandardCheckoutPayRequest.build_request(merchant_order_id=unique_order_id,
                                                                    amount=payload.amount*100,
                                                                    redirect_url=ui_redirect_url)
    standard_pay_response = client.pay(standard_pay_request)
    checkout_page_url = standard_pay_response.redirect_url
    print(standard_pay_response)

    return {
        "order_id": standard_pay_response.order_id,
        "state": standard_pay_response.state,
        "expire_at":standard_pay_response.expire_at,
        "checkout_page_url":standard_pay_response.redirect_url,
    }

from django.http import HttpResponse
from requests.exceptions import JSONDecodeError, RequestException

logger = logging.getLogger(__name__)

@router.post("/verify-payment")
def verify_payment(request, payload: VerifyPaymentPayload):
    """Verify Payment Status"""
    global client

    if client !=None:
        client = create_client()

    try:
        # Call PhonePe API to get order status
        order_status_response = client.get_order_status(merchant_order_id=payload.order_id)
        logger.info(f"Order Status Response: {order_status_response}")
        
        # Check if the response indicates success
        if not order_status_response.success:
            logger.warning(f"Payment verification failed: {order_status_response.message}")
            return HttpResponse(
                {"message": f"Payment verification failed: {order_status_response.message}"},
                status=400
            )
        
        # Return the order state
        return {"state": order_status_response.state}

    except JSONDecodeError as e:
        # Log the raw response for debugging
        logger.error(f"JSON Decode Error: {str(e)}")
        try:
            # Attempt to fetch raw response manually (bypass SDK parsing)
            raw_response = client._request_via_auth_refresh(
                method="GET",
                url=f"{client.base_url}/pg/v2/order/status/{payload.order_id}",
                path_params={"orderDetails": payload.order_id},
                response_obj=None
            )
            logger.error(f"Raw Response: {raw_response.text}, Status Code: {raw_response.status_code}")
            return HttpResponse(
                {"message": "Invalid response from payment gateway", "details": raw_response.text},
                status=500
            )
        except Exception as inner_e:
            logger.error(f"Failed to fetch raw response: {str(inner_e)}")
            return HttpResponse(
                {"message": "Invalid response from payment gateway"},
                status=500
            )

    except RequestException as e:
        logger.error(f"Request Error: {str(e)}")
        return HttpResponse(
            {"message": "Payment gateway unavailable"},
            status=503
        )

    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return HttpResponse(
            {"message": "Internal server error", "details": str(e)},
            status=500
        )