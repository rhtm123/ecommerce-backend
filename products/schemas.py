
from datetime import datetime
from typing import Optional
from ninja import Schema


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
    category_id: int
    created: datetime
    updated: datetime

class ProductCreateSchema(Schema):
    name: str
    description: Optional[str] = None
    base_price: float
    category_id: int

class ProductUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    category_id: Optional[int] = None


class ProductListingOutSchema(Schema):
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
