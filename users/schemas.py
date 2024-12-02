# schemas.py
from ninja import Schema
from typing import Optional
from datetime import datetime

class UserCreateSchema(Schema):
    username: str
    password: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    role: Optional[str] = 'buyer'

class UserUpdateSchema(Schema):
    email: Optional[str] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    role: Optional[str] = None

class UserOutSchema(Schema):
    id: int
    username: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    role: str
    created: datetime
    updated: datetime


class EntityOutSchema(Schema):
    id: int
    name: str 
    gst_number: Optional[str] = None
    user: UserOutSchema | None = None
    created: datetime
    updated: datetime


class EntityCreateSchema(Schema):
    user_id: int
    name: str
    address_id: Optional[int] = None
    gst_number: Optional[str] = None


class EntityUpdateSchema(Schema):
    name: Optional[str] = None
    gst_number: Optional[str] = None


###### shipping Address 

class ShippingAddressOutSchema(Schema):
    id: int
    user_id: Optional[int] = None
    address_id: Optional[int] = None
    is_default: bool
    created: datetime
    updated: datetime


class ShippingAddressCreateSchema(Schema):
    user_id: Optional[int] = None
    address_id: Optional[int] = None
    is_default: Optional[bool] = False


class ShippingAddressUpdateSchema(Schema):
    user_id: Optional[int] = None
    address_id: Optional[int] = None
    is_default: Optional[bool] = None