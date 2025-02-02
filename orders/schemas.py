from datetime import datetime
from typing import List, Optional
from ninja import Schema
from ninja.schema import Field


# from products.schemas import ProductListingOutSchema

class ProductListingSchema(Schema):
    id: int
    name: Optional[str] = None
    slug: str

    price: float
    stock: int
    # rating: Optional[float] = None
    # popularity: Optional[int] = None
    created: datetime
    updated: datetime


class OrderItemOutSchema(Schema):
    id: int
    order_id: int
    product_listing: Optional[ProductListingSchema] = None
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
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime
    # items: List[OrderItemOutSchema]  # Nested items schema

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

