# from datetime import datetime
from typing import Optional
from ninja import Schema
# from ninja.schema import Field


class DeliveryPinOutSchema(Schema):
    id: int
    pin: Optional[str] = None
    estore_id: Optional[int] = None
    cod_available: bool
    city: Optional[str] = None
    state: Optional[str] = None