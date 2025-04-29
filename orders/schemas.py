from datetime import datetime
from typing import List, Optional
from ninja import Schema
from ninja.schema import Field
from decimal import Decimal


from users.schemas import ShippingAddressOutSchema

from products.models import ProductListing

# class AppliedCouponSchema(Schema):
#     id: int
#     code: str
#     discount_type: str
#     discount_value: float
#     discount_amount: float

# class AppliedOfferSchema(Schema):
#     id: int
#     offer_name: str
#     offer_type: str
#     discount_amount: float
#     buy_quantity: int
#     get_quantity: int
#     get_discount_percent: float

class ProductListingSchema(Schema):
    id: int
    name: Optional[str] = None
    slug: str
    price: Optional[float] = None
    mrp: Optional[float] = None
    cgst_rate: Optional[float] = None
    sgst_rate: Optional[float] = None
    igst_rate: Optional[float] = None

    # stock: Optional[int] = None
    # rating: Optional[float] = None
    # popularity: Optional[int] = None
    # created: datetime
    # updated: datetime


class CouponSchema(Schema):
    code: str
    discount_type: str  # 'PERCENTAGE' or 'FIXED'
    discount_value: Decimal
    coupon_type: str  # 'PRODUCT' or 'CART'


class OfferSchema(Schema):
    name: str
    offer_type: str  # 'buy_x_get_y', 'bundle', or 'discount'
    # buy_quantity: Optional[int] = 1
    # get_quantity: Optional[int] = 0
    get_discount_percent: Optional[Decimal] = Decimal('0')



class ReviewOutSchema(Schema):
    id: int
    rating: int
    title: Optional[str]
    comment: Optional[str]
    created: datetime
    updated: datetime



# Add this new schema for user details
class OrderUserSchema(Schema):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    google_picture: Optional[str] = None

# Modify OrderSchema to include user details
class OrderSchema(Schema):
    id: int
    user_id: Optional[int] = None
    user: Optional[OrderUserSchema] = None

# Update OrderItemOutSchema to include order user details
class OrderItemOutSchema(Schema):
    id: int
    order_id: int
    order: OrderSchema
    product_listing: ProductListingSchema
    review: Optional[ReviewOutSchema] = None
    quantity: int
    price: float
    subtotal: float
    status: str
    created: datetime
    updated: datetime

    cancel_requested: bool
    cancel_reason: Optional[str] = None
    cancel_approved: bool


    return_requested: bool
    return_reason: Optional[str] = None
    return_approved:bool



class OrderItemSchema(Schema):
    id: Optional[int] = None
    product_slug: Optional[str] = None
    product_listing_name: Optional[str] = None
    product_main_image: Optional[str] = Field(None, description="URL for the main product image")
    quantity: Optional[int] = 0
    status: Optional[str] = None
    price: Optional[float] = 0
    # original_price: Optional[float] = None
    discount_amount: Optional[float] = 0
    subtotal: Optional[float] = 0
    shipped_date: Optional[datetime] = None
    # applied_offers: Optional[List[AppliedOfferSchema]] = None
    created: Optional[datetime] = None
    



class OrderOutSchema(Schema):
    id: int
    user_id: int
    order_number: Optional[str] = None
    # status: str
    total_amount: float
    # subtotal_amount: float

    total_discount: Optional[float] = 0
    shipping_address_id: Optional[int] = None
    payment_status: str
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime
    items: Optional[List[OrderItemSchema]] = None
    # applied_coupons: Optional[List[AppliedCouponSchema]] = None

    coupon: Optional[CouponSchema] = None 
    offer: Optional[OfferSchema] = None

    discount_amount_coupon: Optional[float] = 0
    discount_amount_offer: Optional[float] = 0


class UserOutSchema(Schema):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    role: str
    created: datetime
    updated: datetime


class OrderOutOneSchema(Schema):
    id: int
    user: Optional[UserOutSchema] = None
    # status: str
    order_number: Optional[str] = None
    total_amount: float
    # subtotal_amount: float
    total_discount: float
    shipping_address: Optional[ShippingAddressOutSchema] = None
    payment_status: str
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime
    items: Optional[List[OrderItemSchema]] = None
    # applied_coupons: Optional[List[AppliedCouponSchema]] = None

class OrderCreateSchema(Schema):
    user_id: int
    shipping_address_id: Optional[int] = None
    estore_id: Optional[int] = None
    # notes: Optional[str] = None
    # discount: Optional[float] = 0.00
    total_amount: Optional[float] = 0.00
    offer_id: Optional[int] = None
    coupon_id: Optional[int] = None

class OrderUpdateSchema(Schema):
    # status: Optional[str] = None
    payment_status: Optional[str] = None
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    discount: Optional[float] = None




####################### Order Item ###########################

class OrderSchema(Schema):
    id: int 
    user_id : int

class OrderItemOutOneSchema(Schema):
    id: int
    order: Optional[OrderSchema] = None
    product_listing: Optional[ProductListingSchema] = None
    review: Optional[ReviewOutSchema] = None
    quantity: int
    price: float
    subtotal: float
    status: Optional[str] = "pending"
    created: datetime
    updated: datetime

    cancel_requested: bool
    cancel_reason: Optional[str] = None
    cancel_approved: bool


    return_requested: bool
    return_reason: Optional[str] = None
    return_approved:bool


# class AppliedOfferCreateSchema(Schema):
#     offer_id: int
#     offer_name: str
#     offer_type: str
#     discount_amount: float
#     buy_quantity: Optional[int] = 1
#     get_quantity: Optional[int] = 0
#     get_discount_percent: Optional[float] = 0

class OrderItemCreateSchema(Schema):
    order_id: int
    product_listing_id: int
    quantity: int
    price: float
    offer_id: Optional[int] = None
    # original_price: Optional[float] = None
    subtotal: float
    discount_amount: Optional[float] = 0
    # applied_offer: Optional[AppliedOfferCreateSchema] = None

class OrderItemUpdateSchema(Schema):
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = None

    cancel_requested: Optional[bool] = None
    cancel_reason: Optional[str] = None
    cancel_approved: Optional[bool] = None


    return_requested: Optional[bool] = None
    return_reason: Optional[str] = None
    return_approved: Optional[bool] = None

# #############

class DeliveryPackageCreateSchema(Schema):
    pass 

class DeliveryPackageUpdateSchema(Schema):
    pass 

class DeliveryPackageOutSchema(Schema):
    id: int 
    status: str
    order_id: int
    tracking_number: str 
    product_listing_count: int 
    total_units: int 
    delivery_out_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None


# class OrderItemSchema(Schema):
#     id: int
#     # order: Optional[OrderSchema] = None
#     product_listing: Optional[ProductListingSchema] = None
#     # review: Optional[ReviewOutSchema] = None
#     # product_listing_product_name: str
#     # quantity: int
#     # price: float
#     # subtotal: float
#     # status: Optional[str] = "pending"
#     created: datetime
#     updated: datetime


class PackageItemOutSchema(Schema):
    id: int 
    package_id: int 
    quantity: int 
    order_item: Optional[OrderItemSchema] = None 



#####



class DeliveryPackageSchema(Schema):
    tracking_number: Optional[str]
    status: str
    product_listing_count: int
    total_units: int
    delivery_out_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    package_items: List[OrderItemSchema]
    created : Optional[datetime] = None

class OrderDeliveryStatusSchema(Schema):
    order_id: int
    order_number: str
    user: str
    total_amount: float
    total_discount: float
    payment_status: str
    packages: List[DeliveryPackageSchema]
    items_without_package: List[OrderItemSchema]
    coupon: Optional[CouponSchema] = None
    offer: Optional[OfferSchema] = None
    discount_amount_coupon: Optional[float] = 0
    discount_amount_offer: Optional[float] = 0


# class AppliedCouponCreateSchema(Schema):
#     order_id: int
#     coupon_code: str
#     discount_type: str
#     discount_value: float
#     discount_amount: float



