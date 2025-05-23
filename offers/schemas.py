from datetime import datetime
from typing import Optional, List
from ninja import Schema
from decimal import Decimal

class CouponBase(Schema):
    code: str
    description: Optional[str] = None
    discount_type: str  # 'PERCENTAGE' or 'FIXED'
    discount_value: Decimal
    coupon_type: str  # 'PRODUCT' or 'CART'
    min_cart_value: Optional[Decimal] = Decimal('0')
    max_discount_amount: Optional[Decimal] = None
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True
    usage_limit: Optional[int] = None
    per_user_limit: Optional[int] = 1

class CouponCreate(CouponBase):
    pass

class CouponUpdate(Schema):
    description: Optional[str] = None
    discount_value: Optional[Decimal] = None
    min_cart_value: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    usage_limit: Optional[int] = None
    per_user_limit: Optional[int] = None

class CouponOut(CouponBase):
    id: int
    used_count: int
    created: datetime
    updated: datetime

class OfferBase(Schema):
    name: str
    description: str
    offer_type: str  # 'buy_x_get_y', 'bundle', or 'discount'
    offer_scope: str  # 'cart' or 'product'
    min_cart_value: Optional[Decimal] = Decimal('0')
    max_discount_amount: Optional[Decimal] = None
    buy_quantity: Optional[int] = 1
    get_quantity: Optional[int] = 0
    get_discount_percent: Optional[Decimal] = Decimal('0')
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True

class OfferCreate(OfferBase):
    pass

class OfferUpdate(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    offer_scope: Optional[str] = None
    min_cart_value: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    buy_quantity: Optional[int] = None
    get_quantity: Optional[int] = None
    get_discount_percent: Optional[Decimal] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

class OfferOut(OfferBase):
    id: int
    created: datetime
    updated: datetime

class ProductOfferCreate(Schema):
    offer_id: int
    product_id: int
    is_primary: Optional[bool] = False
    bundle_quantity: Optional[int] = 1
    bundle_discount_percent: Optional[Decimal] = Decimal('0')

class ProductOfferOut(Schema):
    id: int
    offer: OfferOut
    product_id: int
    is_primary: bool
    bundle_quantity: int
    bundle_discount_percent: Decimal

class CouponValidationResponse(Schema):
    is_valid: bool
    message: str
    discount_amount: Optional[Decimal] = None
    final_price: Optional[Decimal] = None

class OfferValidationRequest(Schema):
    product_ids: List[int]
    quantities: List[int]

class OfferValidationResponse(Schema):
    is_valid: bool
    message: str
    discount_amount: Optional[Decimal] = None
    final_price: Optional[Decimal] = None
    qualifying_products: Optional[List[int]] = None