from ninja import ModelSchema, Schema, Field
# from pydantic import Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class PaymentOutSchema(Schema):
    id: int
    order_id: int
    order_number: str = Field(None, alias="order.order_number")

    amount: Optional[int]

    status: Optional[str] = None
    transaction_id: Optional[str] = None

    payment_url: Optional[str] = None
    payment_method: Optional[str] = None
    
    created: datetime
    updated: datetime

class PaymentCreateSchema(Schema):
    order_id: int
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    payment_gateway: Optional[str] = "PhonePe"
    estore_id: int
    payment_method: Optional[str] = "pg"
