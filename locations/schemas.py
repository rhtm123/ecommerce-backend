
from ninja import Schema
from typing import Optional
from datetime import datetime

from pydantic import Field

############ 5 Address #############
class AddressOutSchema(Schema):
    id: int
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "India"
    pin: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_map_url: Optional[str] = None
    created: datetime
    updated: datetime

class AddressCreateSchema(Schema):
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "India"
    pin: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_map_url: Optional[str] = None


class AddressUpdateSchema(Schema):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    pin: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_map_url: Optional[str] = None

