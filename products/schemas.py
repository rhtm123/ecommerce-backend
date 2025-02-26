
from datetime import datetime
from typing import Optional, List
from ninja import Schema
from ninja.schema import Field

from typing import Dict


from .models import ProductListing, Category, ProductListingImage

from users.schemas import EntityOut2Schema


class CategoryOutSchema(Schema):
    id: int
    name: str

    slug: str
    image: Optional[str] = None

    description: Optional[str] = None
    # feature_names: Optional[dict] = None

    level: int 
    
    created: datetime
    updated: datetime

    @staticmethod
    def resolve_image(obj: Category) -> Optional[str]:
        """
        Resolves the URL for the main image.
        """
        try:
            # print(obj.main_image)
            # print(obj.main_image.url)
            return obj.image.url if obj.image else None
        except:
            return None

class CategorySchema(Schema):
    id: int
    name: str
    slug: str
    level: int
    # created: str
    # updated: str

class CategoryParentChildrenOutSchema(Schema):
    parents: List[CategorySchema]
    children: List[CategorySchema]

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


class VariantSchema(Schema):
    id: int
    name: str
    attributes: Dict  # JSONField in the model, represented as a dict in Python
    created: datetime
    updated: datetime


class ProductOutOneSchema(Schema):
    id: int
    name: str
    about: Optional[str]  # blank=True, null=True in model
    description: Optional[str]  # blank=True, null=True
    important_info: Optional[str]  # blank=True, null=True
    base_price: float   # DecimalField in model
    tax_category: Optional[int]  # ForeignKey, using ID, nullable
    country_of_origin: str
    created: datetime
    updated: datetime
    variants: List[VariantSchema]  # List of variants related to the product

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
    # base_price: float
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    tax_category_id: Optional[int] = None
    country_of_origin: Optional[str] = "India"
    

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
    mrp: float
    stock: int
    rating: Optional[float] = None
    review_count: int
    buy_limit: int

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
    review_count: int
    popularity : Optional[int] = None

    buy_limit: int

    # seller_id: int
    price: float
    mrp: float
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
    product_listing_id: Optional[int] = None
    feature_group: str
    name: str
    value: str
    created: datetime
    updated: datetime


class ProductListingImageOutSchema(Schema):
    id: int 
    product_listing_id: Optional[int] = None
    alt_text: Optional[str] = None

    image: Optional[str] = Field(None, description="URL for the main product image")

    @staticmethod
    def resolve_image(obj: ProductListingImage) -> Optional[str]:
        """
        Resolves the URL for the main image.
        """
        try:
            # print(obj.main_image)
            # print(obj.main_image.url)
            # small_image_url = product.main_image.format(width=300, height=300, crop="fill")

            return obj.image.url if obj.image else None
        except:
            return None