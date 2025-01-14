
from datetime import datetime
from typing import Optional
from ninja import Schema
from ninja.schema import Field

from .models import ProductListing

from users.schemas import EntityOut2Schema


class CategoryOutSchema(Schema):
    id: int
    name: str

    slug: str

    description: Optional[str] = None
    # feature_names: Optional[dict] = None

    level: int 
    
    created: datetime
    updated: datetime

class CategoryCreateSchema(Schema):
    name: str
    description: Optional[str] = None
    # feature_names: Optional[dict] = None
    parent_id: Optional[int] = None
 
class CategoryUpdateSchema(Schema):
    name: Optional[str] = None
    

class FeatureGroupOutSchema(Schema):
    id: int 
    name : str 
    category_id: Optional[int] = None


class FeatureTemplateOutSchema(Schema):
    id: int
    name: Optional[str] = None
    feature_group_id: Optional[int] = None
    key_feature: bool = False
    possible_values: Optional[dict]

    created: datetime
    updated: datetime


class ProductOutSchema(Schema):
    id: int
    name: str
    description: Optional[str] = None
    base_price: float
    # category_id: int
    created: datetime
    updated: datetime

class ProductCreateSchema(Schema):
    name: str
    description: Optional[str] = None
    base_price: float
    # category_id: int

class ProductUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None


class ProductListingOutSchema(Schema):
    id: int
    product_id: Optional[int] = None  # Making it optional as it may be null/blank
    name: Optional[str] = None
    brand: Optional[EntityOut2Schema] = None  # Assuming EntityOutSchema handles the `brand` details
    slug: str

    category: Optional[CategoryOutSchema] = None

    main_image: Optional[str] = Field(None, description="URL for the main product image")
    thumbnail: Optional[str] = Field(None, description="URL for the dynamically generated thumbnail")

    price: float
    stock: int
    rating: Optional[float] = None
    popularity: Optional[int] = None
    created: datetime
    updated: datetime

    @staticmethod
    def resolve_thumbnail(obj: ProductListing) -> Optional[str]:
        """
        Resolves the URL for the dynamically generated thumbnail.
        """
        try:
            return obj.thumbnail.url if obj.thumbnail else None
        except:
            return None

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


class ProductListingOneOutSchema(Schema):
    id: int
    name: Optional[str] = None
    product: Optional[ProductOutSchema] = None
    brand: Optional[EntityOut2Schema] = None
    seller: Optional[EntityOut2Schema] = None
    slug: Optional[str] = None
    category: Optional[CategoryOutSchema] = None

    box_items: Optional[str] = None
    features: Optional[dict] = None

    rating: Optional[float] = None
    popularity : Optional[int] = None



    # seller_id: int
    price: float
    stock: int


    main_image: Optional[str] = Field(None, description="URL for the main product image")
    thumbnail: Optional[str] = Field(None, description="URL for the dynamically generated thumbnail")

    created: datetime
    updated: datetime

    @staticmethod
    def resolve_thumbnail(obj: ProductListing) -> Optional[str]:
        """
        Resolves the URL for the dynamically generated thumbnail.
        """
        try:
            return obj.thumbnail.url if obj.thumbnail else None
        except:
            return None

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

class ProductListingCreateSchema(Schema):
    product_id: int
    # seller_id: int
    price: float
    stock: Optional[int] = 0

class ProductListingUpdateSchema(Schema):
    price: Optional[float] = None
    stock: Optional[int] = None

class FeatureOutSchema(Schema):
    id: int
    listing_id: Optional[int] = None
    feature_group: str
    name: str
    value: str
    created: datetime
    updated: datetime
