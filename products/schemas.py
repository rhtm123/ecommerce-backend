
from datetime import datetime
from typing import Optional
from ninja import Schema
from ninja.schema import Field

from .models import ProductListing

from users.schemas import EntityOutSchema


class CategoryOutSchema(Schema):
    id: int
    name: str

    description: Optional[str] = None
    feature_names: Optional[dict] = None

    level: int 
    
    created: datetime
    updated: datetime

class CategoryCreateSchema(Schema):
    name: str
    description: Optional[str] = None
    feature_names: Optional[dict] = None
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
    # category_id: Optional[int] = None


    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_listings', null=True, blank=True)
    # name = models.CharField(max_length=255, null=True, blank=True)
    # category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category_listings', null=True, blank=True)
    # brand = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="brand_product_listings", null=True, blank=True)
    # manufacturer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="manufacturer_product_listings", null=True, blank=True)


    # slug = models.SlugField(default="", null=False, blank=True)

    # box_items = models.TextField(null=True, blank=True)
    # features = models.JSONField(null=True, blank=True)
    # # features example -> {"general": [{"name":"ram", "value":"6gb"}, {'name':"storage, "value":"128gb"}], "camera": [{"name":"front camera", "value":"40mp"]} 
    # approved = models.BooleanField(default=False)

    # listed = models.BooleanField(default=False)

    # main_image = ProcessedImageField(
    #     upload_to="kb/product_listings/",
    #     processors=[ResizeToFill(1200, 1200)],  # Resize to 800x800 pixels
    #     format="WEBP",
    #     options={"quality": 85},  # Save with 85% quality
    #     null=True, blank=True
    # )

    # thumbnail = ImageSpecField(source='main_image',
    #                                   processors=[ResizeToFill(360, 360)],
    #                                   format='WEBP',)

    # # features text // json
    # variant = models.OneToOneField(Variant, on_delete=models.SET_NULL, related_name="variant_listing", null=True, blank=True)
    # seller = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name='seller_listings', null=True, blank=True)
    # packer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="packer_listings", null=True, blank=True)
    # importer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="importer_listings", null=True, blank=True)
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)



class ProductListingOutSchema(Schema):
    id: int
    product_id: Optional[int] = None  # Making it optional as it may be null/blank
    name: Optional[str] = None
    brand: Optional[EntityOutSchema] = None  # Assuming EntityOutSchema handles the `brand` details
    slug: str

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
        if obj.thumbnail:
            return obj.thumbnail.url  # Ensure the thumbnail URL is returned
        return None

    @staticmethod
    def resolve_main_image(obj: ProductListing) -> Optional[str]:
        """
        Resolves the URL for the main image.
        """
        if obj.main_image:
            return obj.main_image.url  # Ensure the main image URL is returned
        return None

class ProductListingOneOutSchema(Schema):
    id: int
    product_id: int
    # seller_id: int
    price: float
    stock: int
    created: datetime
    updated: datetime

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
