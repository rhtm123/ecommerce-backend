from ninja import  Router

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

from django.core.cache import cache

import plivo

router = Router()


from django.contrib.auth import authenticate
from utils.cache import cache_response


from ninja_jwt.tokens import RefreshToken


from ninja_jwt.authentication import JWTAuth

from google.oauth2 import id_token
from google.auth.transport import requests


from ninja.security import HttpBearer
from pydantic import BaseModel

# from twilio.request_validator import RequestValidator
# from twilio.twiml.messaging_response import MessagingResponse

from utils.send_whatsapp import send_wa_msg, send_wa_msg_plivo
from utils.constants import wa_content_templates, wa_plivo_templates

from django.http import JsonResponse




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

    # content_template_sid = wa_content_templates["mobile_verify_sid"]
    # variables = {'1': otp}
    # send_wa_msg(content_template_sid, variables, phone_number)

    template_name = wa_plivo_templates["mobile_verify_sid"]
    variables = [otp]
    send_wa_msg_plivo(template_name, variables, phone_number)

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



@router.post("/plivo/webhook/")
def whatsapp_webhook(request):
    """Handle incoming WhatsApp messages from Plivo."""
    print("Webhook is called!")

    try:
        # Capture form-encoded POST data (Plivo sends x-www-form-urlencoded by default)
        data = request.POST.dict() if hasattr(request, "POST") else request.body
        print("Received webhook payload:", data)

        # Extract basic WhatsApp message fields
        from_number = data.get("From", "")
        to_number = data.get("To", "")
        message_content = data.get("Body", "")
        message_uuid = data.get("MessageUUID", "")
        timestamp = data.get("MessageTime", "")

        # Log message details
        print(f"From: {from_number}, To: {to_number}, Body: {message_content}, UUID: {message_uuid}, Time: {timestamp}")

        # Initialize Plivo client (if you want to reply, etc.)
        AUTH_ID = config("PLIVO_AUTH_ID")
        AUTH_TOKEN = config("PLIVO_AUTH_TOKEN")
        client = plivo.RestClient(AUTH_ID, AUTH_TOKEN)

        # You could respond or trigger business logic here if needed

        return JsonResponse({"status": "success", "message": "Webhook received"}, status=200)

    except Exception as e:
        print("Error processing webhook:", str(e))
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    


def set_refresh_cookie(response, refresh_token):
    
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        secure=True,
        samesite='None',  # Or 'Lax' if needed
        max_age=20 * 24 * 60 * 60,  # 20 days
        # path='/'  # Scoped only to refresh endpoint
    )
    # print("cookies set");

@router.post("/token/refresh", tags=['token'])
def refresh_token_view(request):
    try:
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return JsonResponse({"status": "error", "message": "No refresh token provided"}, status=401)

        # Create a RefreshToken instance
        refresh = RefreshToken(refresh_token)

        # Generate new access token
        access_token = str(refresh.access_token)

        return JsonResponse({"access_token": access_token})
    except Exception as e:
        return JsonResponse({"error": "Token is invalid or expired"}, status=401)

    
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

        # print(refresh)

        response = JsonResponse({
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "google_picture": user.google_picture,
            "last_name": user.last_name,
            "access_token": access_token,
            "entity": entity,
            "mobile_verified": user.mobile_verified,
            "mobile": user.mobile,
            "gender": user.gender,
        })

        set_refresh_cookie(response, refresh)
        return response

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

        response = JsonResponse({
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "google_picture": user.google_picture,
            "last_name": user.last_name,
            "access_token": access_token,
            "entity": entity,
            "mobile_verified": user.mobile_verified,
            "mobile": user.mobile,
            "gender": user.gender,
        })

        set_refresh_cookie(response, refresh)
        return response
    
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
def users(request,  page: int = 1, page_size: int = 10, search: str = None, role:str = None , ordering: str = None, estore_id: int = None):
    qs = User.objects.all()
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



    return paginate_queryset(request, qs, UserOutSchema, page, page_size)

# Read Single User (Retrieve)
@router.get("/users/{user_id}/", response=UserOutSchema)
@cache_response()
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
@cache_response()
def entities(request,  page: int = 1, 
             page_size: int = 10, 
             search: str = None, 
             entity_type:str = None , 
             ordering: str = None,
             featured: bool = None,
             ):
    qs = Entity.objects.all()
    

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

    if featured is not None:
        qs = qs.filter(featured=featured)
        query = query + "&featured=" + str(featured)


    return paginate_queryset(request, qs, EntityOutSchema, page, page_size, query)

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
@cache_response()
def shipping_addresses(request,  page: int = 1, page_size: int = 10, user_id:int = None , is_default: bool = None, ordering: str = None,):
    qs = ShippingAddress.objects.all()


    if user_id:
        qs = qs.filter(user__id=user_id)

    if is_default:
        qs = qs.filter(is_default=is_default)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, ShippingAddressOutSchema, page, page_size)

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