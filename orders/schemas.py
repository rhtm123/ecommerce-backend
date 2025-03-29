from datetime import datetime
from typing import List, Optional
from ninja import Schema
from ninja.schema import Field

from users.schemas import ShippingAddressOutSchema


# from products.schemas import ProductListingOutSchema

class ProductListingSchema(Schema):
    id: int
    name: Optional[str] = None
    slug: str

    price: Optional[float] = None
    mrp: Optional[float] = None

    cgst_rate: float = Field(None, alias='tax_category.cgst_rate')
    sgst_rate: float = Field(None, alias='tax_category.sgst_rate')
    igst_rate: float = Field(None, alias='tax_category.igst_rate')


    # stock: Optional[int] = None
    # rating: Optional[float] = None
    # popularity: Optional[int] = None
    # created: datetime
    # updated: datetime



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



class OrderItemSchema(Schema):
    id: int
    product_listing_name: Optional[str] = None 
    quantity: Optional[int] = None
    status: Optional[str] = None
    price: Optional[float] = None

    subtotal: Optional[float] = None

    shipped_date: Optional[datetime] = None

class OrderOutSchema(Schema):
    id: int
    user_id: int
    order_number: Optional[str] = None
    # status: str
    total_amount: float
    shipping_address_id: Optional[int] = None
    payment_status: str
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime

    items: Optional[List[OrderItemSchema]] = None  # Include only if `items_needed=True`


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
    shipping_address: Optional[ShippingAddressOutSchema] = None
    payment_status: str
    # tracking_number: Optional[str] = None
    notes: Optional[str] = None
    # discount: float
    created: datetime
    updated: datetime

class OrderCreateSchema(Schema):
    user_id: int
    shipping_address_id: Optional[int] = None
    estore_id: Optional[int] = None
    # notes: Optional[str] = None
    # discount: Optional[float] = 0.00
    total_amount: Optional[float] = 0.00

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
    # product_listing_product_name: str
    quantity: int
    price: float
    subtotal: float
    status: Optional[str] = "pending"
    created: datetime
    updated: datetime


class OrderItemCreateSchema(Schema):
    order_id: int
    product_listing_id: int
    quantity: int
    price: float
    subtotal: float

class OrderItemUpdateSchema(Schema):
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: str

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


class OrderItemSchema(Schema):
    id: int
    # order: Optional[OrderSchema] = None
    product_listing: Optional[ProductListingSchema] = None
    # review: Optional[ReviewOutSchema] = None
    # product_listing_product_name: str
    # quantity: int
    # price: float
    # subtotal: float
    # status: Optional[str] = "pending"
    created: datetime
    updated: datetime


class PackageItemOutSchema(Schema):
    id: int 
    package_id: int 
    quantity: int 
    order_item: Optional[OrderItemSchema] = None 



#####



class OrderItemSchema(Schema):
    product_listing: str
    quantity: int
    status: str
    price: float
    subtotal: float
    created: datetime
    shipped_date: Optional[datetime] = None


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
    payment_status: str
    packages: List[DeliveryPackageSchema]
    items_without_package: List[OrderItemSchema]
    


