from datetime import datetime
from typing import List, Optional
from ninja import Schema
from ninja.schema import Field


from users.schemas import ShippingAddressOutSchema


# from products.schemas import ProductListingOutSchema

class ProductListingSchema(Schema):
    id: int
    name: Optional[str] = None
    slug: str

    price: Optional[float] = None
    stock: Optional[int] = None
    # rating: Optional[float] = None
    # popularity: Optional[int] = None
    # created: datetime
    # updated: datetime



class ReviewOutSchema(Schema):
    id: int
    rating: int
    title: Optional[str]
    comment: Optional[str]
    created: datetime
    updated: datetime


class OrderItemOutSchema(Schema):
    id: int
    order_id: int
    product_listing: Optional[ProductListingSchema] = None

    review: Optional[ReviewOutSchema] = None
    # product_listing_product_name: str
    quantity: int
    price: float
    subtotal: float
    status: Optional[str] = "pending"
    created: datetime
    updated: datetime



class OrderOutSchema(Schema):
    id: int
    user_id: int
    status: str
    total_amount: float
    shipping_address_id: Optional[int] = None
    payment_status: str
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime
    # items: List[OrderItemOutSchema]  # Nested items schema


class UserOutSchema(Schema):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    role: str
    created: datetime
    updated: datetime


class OrderOutOneSchema(Schema):
    id: int
    user: Optional[UserOutSchema] = None
    status: str
    total_amount: float
    shipping_address: Optional[ShippingAddressOutSchema] = None
    payment_status: str
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime

class OrderCreateSchema(Schema):
    user_id: int
    shipping_address_id: Optional[int] = None
    estore_id: Optional[int] = None
    # notes: Optional[str] = None
    # discount: Optional[float] = 0.00
    total_amount: Optional[float] = 0.00

class OrderUpdateSchema(Schema):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    discount: Optional[float] = None



####################### Order Item ###########################

class OrderSchema(Schema):
    id: int 
    user_id : int

class OrderItemOutOneSchema(Schema):
    id: int
    order: Optional[OrderSchema] = None
    product_listing: Optional[ProductListingSchema] = None
    review: Optional[ReviewOutSchema] = None
    # product_listing_product_name: str
    quantity: int
    price: float
    subtotal: float
    status: Optional[str] = "pending"
    created: datetime
    updated: datetime


class OrderItemCreateSchema(Schema):
    order_id: int
    product_listing_id: int
    quantity: int
    price: float
    subtotal: float

class OrderItemUpdateSchema(Schema):
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: str

