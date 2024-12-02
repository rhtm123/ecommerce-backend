
from datetime import datetime
from typing import Optional
from ninja import Schema


class CategoryOutSchema(Schema):
    id: int
    name: str
    parent_id: Optional[int] = None
    created: datetime
    updated: datetime

class CategoryCreateSchema(Schema):
    name: str
    parent_id: Optional[int] = None

class CategoryUpdateSchema(Schema):
    name: Optional[str] = None
    parent_id: Optional[int] = None




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
