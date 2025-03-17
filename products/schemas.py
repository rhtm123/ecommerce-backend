
from datetime import datetime
from typing import Optional, List
from ninja import Schema, ModelSchema
from ninja.schema import Field

from typing import Dict


from .models import ReturnExchangePolicy, ProductListing, Category, ProductListingImage

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
    about: Optional[str] = None
    description: Optional[str] = None
    important_info: Optional[str] = None
    # base_price: Optional[float] = 0
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    tax_category_id: Optional[int] = None
    country_of_origin: Optional[str] = "India"

class ProductUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    tax_category_id: Optional[int] = None
    base_price: Optional[float] = None


class ProductListingOutSchema(Schema):
    id: int
    product_id: Optional[int] = None  # Making it optional as it may be null/blank
    name: Optional[str] = None
    brand: Optional[EntityOut2Schema] = None  # Assuming EntityOutSchema handles the `brand` details
    slug: str
    seller_id : Optional[int] = None

    category: Optional[CategoryOutSchema] = None

    approved: Optional[bool] 

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


class ReturnExchangePolicySchema(ModelSchema):
    class Meta:
        model = ReturnExchangePolicy
        fields = ['id', 'name', 'return_available', 'exchange_available', 'return_days', 'exchange_days', 'conditions']


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

    return_exchange_policy: Optional[ReturnExchangePolicySchema] = None

    buy_limit: int
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
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    tax_category_id: Optional[int] = None
    return_exchange_policy_id: Optional[int] = None
    estore_id: Optional[int] = None
    box_items: Optional[str] = None
    features: Optional[dict] = None
    approved: Optional[bool] = False
    featured: Optional[bool] = False
    variant_id: Optional[int] = None
    seller_id: Optional[int] = None
    packer_id: Optional[int] = None
    importer_id: Optional[int] = None
    price: float
    mrp: Optional[float] = None
    stock: Optional[int] = 0
    buy_limit: Optional[int] = 10
    rating: Optional[float] = 5.0
    review_count: Optional[int] = 1
    popularity: Optional[int] = 100
    main_image: Optional[str] = None

class ProductListingUpdateSchema(Schema):
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    tax_category_id: Optional[int] = None
    return_exchange_policy_id: Optional[int] = None
    box_items: Optional[str] = None
    features: Optional[dict] = None
    approved: Optional[bool] = None
    featured: Optional[bool] = None
    variant_id: Optional[int] = None
    seller_id: Optional[int] = None
    packer_id: Optional[int] = None
    importer_id: Optional[int] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    stock: Optional[int] = None
    buy_limit: Optional[int] = None

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

class VariantCreateSchema(Schema):
    product_id: int
    name: str
    attributes: Dict

class VariantUpdateSchema(Schema):
    name: Optional[str] = None
    attributes: Optional[Dict] = None

class ProductListingImageCreateSchema(Schema):
    product_listing_id: int
    image: str
    alt_text: Optional[str] = None

class ProductListingImageUpdateSchema(Schema):
    alt_text: Optional[str] = None
    image: Optional[str] = None

class FeatureCreateSchema(Schema):
    product_listing_id: int
    feature_group: str
    feature_template_id: Optional[int] = None
    value: str

class FeatureUpdateSchema(Schema):
    feature_group: Optional[str] = None
    feature_template_id: Optional[int] = None
    value: Optional[str] = None

class FeatureGroupCreateSchema(Schema):
    name: str
    category_id: Optional[int] = None

class FeatureTemplateCreateSchema(Schema):
    name: str
    feature_group_id: Optional[int] = None
    key_feature: Optional[bool] = False
    possible_values: Optional[dict] = None