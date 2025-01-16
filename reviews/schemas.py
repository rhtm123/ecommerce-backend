

from datetime import datetime
from typing import Optional, List
from ninja import Schema
from ninja.schema import Field

from users.schemas import UserOutSchema



class ReviewOutSchema(Schema):
    id: int
    user: Optional[UserOutSchema] = None
    product_listing_id: int
    comment: Optional[str] = None
    rating: int

    created: datetime
    updated: datetime

class ReviewCreateSchema(Schema):
    comment: Optional[str] = None
    user_id: Optional[int] = None
    product_listing_id: int
    rating: int


 
class ReviewUpdateSchema(Schema):
    comment: Optional[str] = None