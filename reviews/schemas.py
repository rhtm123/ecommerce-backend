

from datetime import datetime
from typing import Optional, List
from ninja import Schema
from ninja.schema import Field

from users.schemas import UserOutSchema

from products.models import ProductListing


class ProductListingSchema(Schema):
    name: str = None
    # main_image: Optional[str] = None

    main_image: Optional[str] = Field(None, description="URL for the main product image")

    @staticmethod
    def resolve_main_image(obj: ProductListing) -> Optional[str]:
        """
        Resolves the URL for the main image.
        """
        try:
            # print(obj.main_image)
            # print(obj.main_image.url)
            return obj.main_image.url if obj.main_image else None
        except:
            return None



class ReviewOutSchema(Schema):
    id: int
    user: Optional[UserOutSchema] = None
    product_listing_id: int
    product_listing: Optional[ProductListingSchema] = None
    comment: Optional[str] = None
    title: Optional[str] = None
    order_item_id: Optional[int] = None
    rating: int

    created: datetime
    updated: datetime

class ReviewCreateSchema(Schema):
    comment: Optional[str] = None
    user_id: Optional[int] = None
    product_listing_id: int
    order_item_id: Optional[int]
    rating: int
    title: Optional[str] = None



 
class ReviewUpdateSchema(Schema):
    comment: Optional[str] = None
    title: Optional[str] = None
    rating: Optional[int] = None

