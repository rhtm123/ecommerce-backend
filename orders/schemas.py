from datetime import datetime
from typing import List, Optional
from ninja import Schema


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
    created_at: datetime
    updated_at: datetime
    # items: List['OrderItemOutSchema']  # Nested items schema

class OrderCreateSchema(Schema):
    user_id: int
    shipping_address_id: Optional[int] = None
    notes: Optional[str] = None
    discount: Optional[float] = 0.00

class OrderUpdateSchema(Schema):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    discount: Optional[float] = None


####################### Order Item ###########################

class OrderItemOutSchema(Schema):
    id: int
    order_id: int
    product_listing_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

class OrderItemCreateSchema(Schema):
    order_id: int
    product_listing_id: int
    product_name: str
    quantity: int
    price: float

class OrderItemUpdateSchema(Schema):
    quantity: Optional[int] = None
    price: Optional[float] = None
