from ninja import  Router, Query, Schema

# router.py
from .models import User, Entity, ShippingAddress
from .schemas import UserCreateSchema, UserUpdateSchema, UserOutSchema
from .schemas import EntityCreateSchema, EntityUpdateSchema, EntityOutSchema, EntityOutOneSchema
from .schemas import ShippingAddressCreateSchema, ShippingAddressUpdateSchema, ShippingAddressOutSchema


from django.contrib.auth.hashers import make_password
from typing import List
from django.shortcuts import get_object_or_404

from utils.pagination import PaginatedResponseSchema, paginate_queryset
from decouple import config

router = Router()


from django.contrib.auth import authenticate


from ninja_jwt.tokens import RefreshToken

from ninja_jwt.authentication import JWTAuth

from google.oauth2 import id_token
from google.auth.transport import requests


from ninja.security import HttpBearer
from pydantic import BaseModel

from django.conf import settings
from django.http import HttpResponse
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from utils.send_whatsapp import send_wa_msg
from utils.constants import wa_content_templates



GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')

from users.models import User, MobileVerification
from pydantic import BaseModel

from utils.generate import generate_otp


class OTPRequestSchema(BaseModel):
    mobile: str

class OTPVerifySchema(BaseModel):
    mobile: str
    otp: str


@router.post("/send-otp/")
def send_otp_api(request, data: OTPRequestSchema):
    phone_number = data.mobile

    otp = generate_otp()

    content_template_sid = wa_content_templates["mobile_verify_sid"]
    variables = {'1': otp}
    send_wa_msg(content_template_sid, variables, phone_number)
    # print("WA message sent!!")

    MobileVerification.objects.update_or_create(
        mobile=phone_number,
        defaults={'otp': otp}
    )

    return {"message": "OTP sent successfully"}

@router.post("/verify-otp/")
def verify_otp_api(request, data: OTPVerifySchema):
    mobile = data.mobile
    otp = data.otp

    otp_entry = get_object_or_404(MobileVerification, mobile=mobile)

    if otp_entry.otp == otp:
        otp_entry.delete()  # Remove OTP after successful verification
        try:
            user_obj = User.objects.get(mobile=mobile)
            user_obj.mobile_verified = True
            user_obj.save()
        except:
            pass

        return {"message": "OTP verified successfully"}
    return {"error": "Invalid or expired OTP"}



# @router.post("/plivo/webhook/")
# def whatsapp_webhook(request):
#     """Handle incoming WhatsApp messages from Plivo."""
#     print("Web hook is called now!!")
#     try:
#         # Get raw JSON payload
#         data = request.POST.dict()
#         print("Received webhook payload: %s", data)

#         import plivo
#         AUTH_ID=<AUTH_ID>
#         AUTH_TOKEN=<AUTH_TOKEN>
#         client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)

#         # if not data:
#         #     return JsonResponse({"status": "error", "message": "No payload received"}, status=400)

#         # Extract fields (no strict schema validation here for simplicity)
#         from_number = data.get("From", "unknown")
#         to_number = data.get("To", "unknown")
#         message_content = data.get("Body", "unknown")
#         # message_uuid = data.get("MessageUUID", "unknown")
#         # timestamp = data.get("MessageTime", "unknown")

#         try:
#             response = client.messages.create(
#                 src=to_number,  # Your WhatsApp number
#                 dst=from_number,  # Sender's number
#                 type_="whatsapp",
#                 text=f"Thanks for your message: {message_content}"
#             )
#         except plivo.exceptions.PlivoRestError as e:
#             print(f"Failed to send reply: {e}")
#         return {"status": "success", "message": "Webhook received"}

#     except Exception as e:
#         print(f"Webhook processing error: {e}")
#         return {"status": "error", "message": str(e)}
    


@router.post("/twilio/webhook/")
def twilio_whatsapp_webhook(request):
    """Handles incoming WhatsApp messages from Twilio"""


    try:
        # Verify Twilio request
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        signature = request.headers.get("X-Twilio-Signature", "")

        url = request.build_absolute_uri()
        post_data = request.POST.dict()  # Convert QueryDict to a standard dict

        # print(url)
        # print(signature)
        # print(post_data)
      
        if not validator.validate(url, post_data, signature):
            print("Unauthorized request attempt - Signature validation failed!")
            return HttpResponse("Unauthorized", status=403)

        # Process Incoming Message
        from_number = post_data.get("From", "")
        body = post_data.get("Body", "").strip().lower()

        # Auto-response logic
        response = MessagingResponse()
        if "hello" in body:
            response.message("Hi there! How can I assist you today?")
        else:
            response.message("Sorry, I didn't understand that. Type 'hello' to start.")

        return HttpResponse(str(response), content_type="application/xml")

    except Exception as e:
        # logger.error(f"Error processing webhook: {e}")
        return HttpResponse("Internal Server Error", status=500)
    
class TokenSchema(BaseModel):
    token: str

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            return idinfo
        except ValueError:
            return None


class UserLoginSchema(BaseModel):
    username: str
    password: str


@router.post("/auth/login/", tags=['token'])
def auth_login(request, payload: UserLoginSchema):
    try:
 
        # Check if the user exists in the database, if not, create them
        user = authenticate(username=payload.username, password=payload.password)

        if user is None:
            return {"error": "Invalid credentials"} 

        entity = None
        try: 
            entity_object = Entity.objects.get(user=user)
            entity = {
                "id": entity_object.id,
                "entity_type": entity_object.entity_type,
                "name": entity_object.name,
            }

        except:
            pass

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "google_picture": user.google_picture,
            "last_name":user.last_name,
            "access_token": access_token,
            "refresh_token": str(refresh),
            "entity": entity,
            "mobile_verified": user.mobile_verified,
            "mobile": user.mobile,
            "gender": user.gender,
        }
    except:
        return {"error": "Invalid credentials"}
    

@router.post("/auth/google/", tags=['token'])
def google_auth(request, payload: TokenSchema):
    try:
        # Validate Google ID token
        idinfo = id_token.verify_oauth2_token(payload.token, requests.Request(), GOOGLE_CLIENT_ID)
        
        if "email" not in idinfo or not idinfo.get("email_verified"):
            return {"error": "Invalid Google account"}

        email = idinfo["email"]

        first_name = idinfo.get("given_name", "")  # Default to empty string if not provided
        last_name = idinfo.get("family_name", "")  # Default to empty string if not provided
        google_picture = idinfo.get("picture", "") # Default to empty

        # Check if the user exists in the database, if not, create them
        user, created = User.objects.get_or_create(username=email, defaults={"email": email})

        if created:
            user.first_name = first_name
            user.last_name = last_name
            user.google_picture = google_picture
            user.save()

        entity = None
        try: 
            entity_object = Entity.objects.get(user=user)
            entity = {
                "id": entity_object.id,
                "entity_type": entity_object.entity_type,
                "name": entity_object.name,
            }

        except:
            pass

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "google_picture": user.google_picture,
            "last_name":user.last_name,
            "access_token": access_token,
            "refresh_token": str(refresh),
            "entity": entity,
            "mobile_verified": user.mobile_verified,
            "mobile": user.mobile,
            "gender": user.gender,
        }
    
    except ValueError:
        return {"error": "Invalid Google token"}

# Create User
@router.post("/users/", response=UserOutSchema)
def create_user(request, payload: UserCreateSchema):
    user = User(
        username=payload.username,
        email=payload.email,
        mobile=payload.mobile,
        alternate_mobile=payload.alternate_mobile,
        role=payload.role,
        password=make_password(payload.password)  # Hash the password
    )
    user.save()
    return user

# Read Users (List)
@router.get("/users/", response=PaginatedResponseSchema)
def users(request,  page: int = Query(1), page_size: int = Query(10), search: str = None, role:str = None , ordering: str = None, estore_id: int = None):
    qs = User.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if estore_id:
        qs = qs.filter(estore__id=estore_id)
        query = query + "&estore_id=" + str(estore_id)

    if role:
        qs = qs.filter(role=role)
        query = query + "&role=" + role

    if search:
        qs = qs.filter(mobile__icontains=search)
        query = query + "&search=" + search

    
    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering



    return paginate_queryset(request, qs, UserOutSchema, page_number, page_size)

# Read Single User (Retrieve)
@router.get("/users/{user_id}/", response=UserOutSchema)
def retrieve_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user

# Update User
@router.put("/users/{user_id}/", response=UserOutSchema, auth=JWTAuth())
def update_user(request, user_id: int, payload: UserUpdateSchema):
    user = get_object_or_404(User, id=user_id)

    print(payload.dict());
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(user, attr, value)
    user.save()
    return user

# Delete User
@router.delete("/users/{user_id}/")
def delete_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"success": True}





# Create Entity
@router.post("/entities/", response=EntityOutOneSchema)
def create_entity(request, payload: EntityCreateSchema):
    entity = Entity(**payload.dict())

    entity.save()
    return entity

# Read Users (List)
@router.get("/entities/", response=PaginatedResponseSchema)
def entities(request,  page: int = Query(1), page_size: int = Query(10), search: str = None, entity_type:str = None , ordering: str = None,):
    qs = Entity.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if entity_type:
        qs = qs.filter(entity_type=entity_type)
        query = query + "&entity_type=" + entity_type
        

    if search:
        qs = qs.filter(name__icontains=search)
        query = query + "&search=" + search

    
    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering


    return paginate_queryset(request, qs, EntityOutSchema, page_number, page_size, query)

# Read Single User (Retrieve)
@router.get("/entities/{entity_id}/", response=EntityOutOneSchema)
def retrieve_entity(request, entity_id: int):
    entity = get_object_or_404(Entity, id=entity_id)
    return entity

# Update User
@router.put("/entities/{entity_id}/", response=EntityOutSchema)
def update_entity(request, entity_id: int, payload: EntityUpdateSchema):
    entity = get_object_or_404(Entity, id=entity_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(entity, attr, value)
    entity.save()
    return entity

# Delete User
@router.delete("/entities/{entity_id}/")
def delete_entity(request, entity_id: int):
    entity = get_object_or_404(Entity, id=entity_id)
    entity.delete()
    return {"success": True}


######################### Shipping Address #################



@router.post("/shipping-addresses/", response=ShippingAddressOutSchema, auth=JWTAuth())
def create_shipping_address(request, payload: ShippingAddressCreateSchema):

    shipping_address = ShippingAddress(**payload.dict())   
    shipping_address.save()
    return shipping_address

# Read ShippingAddresss (List)
@router.get("/shipping-addresses/", response=PaginatedResponseSchema)
def shipping_addresses(request,  page: int = Query(1), page_size: int = Query(10), user_id:int = None , is_default: bool = None, ordering: str = None,):
    qs = ShippingAddress.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if user_id:
        qs = qs.filter(user__id=user_id)

    if is_default:
        qs = qs.filter(is_default=is_default)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, ShippingAddressOutSchema, page_number, page_size)

# Read Single ShippingAddress (Retrieve)
@router.get("/shipping-addresses/{shipping_address_id}/", response=ShippingAddressOutSchema)
def retrieve_shipping_address(request, shipping_address_id: int):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    return shipping_address

# Update ShippingAddress
@router.put("/shipping-addresses/{shipping_address_id}/", response=ShippingAddressOutSchema)
def update_shipping_address(request, shipping_address_id: int, payload: ShippingAddressUpdateSchema):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(shipping_address, attr, value)
    shipping_address.save()
    return shipping_address

# Delete ShippingAddress
@router.delete("/shipping-addresses/{shipping_address_id}/", auth=JWTAuth())
def delete_shipping_address(request, shipping_address_id: int):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    shipping_address.delete()
    return {"success": True}