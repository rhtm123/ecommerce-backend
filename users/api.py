from ninja import  Router, Query

# router.py
from .models import User, Seller, ShippingAddress
from .schemas import UserCreateSchema, UserUpdateSchema, UserOutSchema
from .schemas import SellerCreateSchema, SellerUpdateSchema, SellerOutSchema
from .schemas import ShippingAddressCreateSchema, ShippingAddressUpdateSchema, ShippingAddressOutSchema


from django.contrib.auth.hashers import make_password
from typing import List
from django.shortcuts import get_object_or_404

from utils.pagination import PaginatedResponseSchema, paginate_queryset

router = Router()

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
def users(request,  page: int = Query(1), page_size: int = Query(10)):
    qs = User.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

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





# Create Seller
@router.post("/sellers/", response=SellerOutSchema)
def create_seller(request, payload: SellerCreateSchema):
    seller = Seller(**payload.dict())

    seller.save()
    return seller

# Read Users (List)
@router.get("/sellers/", response=PaginatedResponseSchema)
def sellers(request,  page: int = Query(1), page_size: int = Query(10)):
    qs = Seller.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    return paginate_queryset(request, qs, SellerOutSchema, page_number, page_size)

# Read Single User (Retrieve)
@router.get("/sellers/{seller_id}/", response=SellerOutSchema)
def retrieve_seller(request, seller_id: int):
    seller = get_object_or_404(Seller, id=seller_id)
    return seller

# Update User
@router.put("/sellers/{seller_id}/", response=SellerOutSchema)
def update_seller(request, seller_id: int, payload: SellerUpdateSchema):
    seller = get_object_or_404(Seller, id=seller_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(seller, attr, value)
    seller.save()
    return seller

# Delete User
@router.delete("/sellers/{seller_id}/")
def delete_seller(request, seller_id: int):
    seller = get_object_or_404(Seller, id=seller_id)
    seller.delete()
    return {"success": True}

######################### Shipping Address #################



@router.post("/shipping_addresses/", response=ShippingAddressOutSchema)
def create_shipping_address(request, payload: ShippingAddressCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    shipping_address = ShippingAddress(**payload.dict())
        
    shipping_address.save()
    return shipping_address

# Read ShippingAddresss (List)
@router.get("/shipping_addresses/", response=PaginatedResponseSchema)
def shipping_addresses(request,  page: int = Query(1), page_size: int = Query(10)):
    qs = ShippingAddress.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

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