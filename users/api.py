from ninja import  Router, Query

# router.py
from .models import User, Entity, ShippingAddress
from .schemas import UserCreateSchema, UserUpdateSchema, UserOutSchema
from .schemas import EntityCreateSchema, EntityUpdateSchema, EntityOutSchema
from .schemas import ShippingAddressCreateSchema, ShippingAddressUpdateSchema, ShippingAddressOutSchema


from django.contrib.auth.hashers import make_password
from typing import List
from django.shortcuts import get_object_or_404

from utils.pagination import PaginatedResponseSchema, paginate_queryset
from decouple import config

router = Router()

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")

from ninja_jwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests

from django.conf import settings

from ninja.security import HttpBearer
from pydantic import BaseModel

from users.models import User

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

        # Check if the user exists in the database, if not, create them
        user, created = User.objects.get_or_create(username=email, defaults={"email": email})

        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return {
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name":user.last_name,
            "access_token": access_token,
            "refresh_token": str(refresh),
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
def users(request,  page: int = Query(1), page_size: int = Query(10), search: str = None, role:str = None , ordering: str = None,):
    qs = User.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if role:
        qs = qs.filter(role=role)

    if search:
        qs = qs.filter(mobile__icontains=search)
    
    if ordering:
        qs = qs.order_by(ordering)


    return paginate_queryset(request, qs, UserOutSchema, page_number, page_size)

# Read Single User (Retrieve)
@router.get("/users/{user_id}/", response=UserOutSchema)
def retrieve_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user

# Update User
@router.put("/users/{user_id}/", response=UserOutSchema)
def update_user(request, user_id: int, payload: UserUpdateSchema):
    user = get_object_or_404(User, id=user_id)
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
@router.post("/entities/", response=EntityOutSchema)
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

    if entity_type:
        qs = qs.filter(entity_type=entity_type)

    if search:
        qs = qs.filter(name__icontains=search)
    
    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, EntityOutSchema, page_number, page_size)

# Read Single User (Retrieve)
@router.get("/entities/{entity_id}/", response=EntityOutSchema)
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



@router.post("/shipping_addresses/", response=ShippingAddressOutSchema)
def create_shipping_address(request, payload: ShippingAddressCreateSchema):

    shipping_address = ShippingAddress(**payload.dict())   
    shipping_address.save()
    return shipping_address

# Read ShippingAddresss (List)
@router.get("/shipping_addresses/", response=PaginatedResponseSchema)
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
@router.get("/shipping_addresses/{shipping_address_id}/", response=ShippingAddressOutSchema)
def retrieve_shipping_address(request, shipping_address_id: int):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    return shipping_address

# Update ShippingAddress
@router.put("/shipping_addresses/{shipping_address_id}/", response=ShippingAddressOutSchema)
def update_shipping_address(request, shipping_address_id: int, payload: ShippingAddressUpdateSchema):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(shipping_address, attr, value)
    shipping_address.save()
    return shipping_address

# Delete ShippingAddress
@router.delete("/shipping_addresses/{shipping_address_id}/")
def delete_shipping_address(request, shipping_address_id: int):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    shipping_address.delete()
    return {"success": True}