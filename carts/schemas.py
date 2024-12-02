from datetime import datetime
from typing import List, Optional

from ninja import Schema


class CartOutSchema(Schema):
    id: int
    user_id: Optional[int] = None
    purchased: bool
    created: datetime
    updated: datetime
    # cart_items: List['CartItemOutSchema']  # Nested items schema

class CartCreateSchema(Schema):
    user_id: Optional[int] = None

class CartUpdateSchema(Schema):
    purchased: Optional[bool] = None



class CartItemOutSchema(Schema):
    id: int
    cart_id: Optional[int] = None
    product_listing_id: Optional[int] = None
    quantity: int
    created: datetime
    updated: datetime

class CartItemCreateSchema(Schema):
    cart_id: Optional[int] = None
    product_listing_id: int
    quantity: Optional[int] = 1

class CartItemUpdateSchema(Schema):
    quantity: Optional[int] = None


class WishlistOutSchema(Schema):
    id: int
    user_id: Optional[int] = None
    name: str
    created: datetime
    updated: datetime
    # wishlist_items: List['WishlistItemOutSchema']  # Nested items schema

class WishlistCreateSchema(Schema):
    user_id: Optional[int] = None
    name: Optional[str] = "My Wishlist"

class WishlistUpdateSchema(Schema):
    name: Optional[str] = None


class WishlistItemOutSchema(Schema):
    id: int
    wishlist_id: Optional[int] = None
    product_listing_id: Optional[int] = None
    created: datetime
    updated: datetime

class WishlistItemCreateSchema(Schema):
    wishlist_id: Optional[int] = None
    product_listing_id: int

class WishlistItemUpdateSchema(Schema):
    # No updatable fields currently; placeholder for future needs
    pass
