from ninja import  Router, Query

# router.py
from .models import Cart, CartItem, Wishlist, WishlistItem


from .schemas import (
    CartCreateSchema, CartOutSchema, CartUpdateSchema,
    CartItemCreateSchema, CartItemUpdateSchema, CartItemOutSchema,
    WishlistCreateSchema, WishlistUpdateSchema, WishlistOutSchema,
    WishlistItemCreateSchema, WishlistItemUpdateSchema, WishlistItemOutSchema
    
)

from django.shortcuts import get_object_or_404

from utils.pagination import PaginatedResponseSchema, paginate_queryset

router = Router()

from ninja_jwt.authentication import JWTAuth


############## 1 city ###########################

######################## Cart #######################


# Create Cart
# @router.post("/carts/", response=CartOutSchema, auth=JWTAuth())
# def create_cart(request, payload: CartCreateSchema):
#     cart = Cart(**payload.dict())
#     cart.save()
#     return cart

@router.post("/carts/", response=CartOutSchema)
def create_cart(request, payload: CartCreateSchema):
    cart = Cart(**payload.dict())
    cart.save()
    return cart

# Read Carts (List)
@router.get("/carts/", response=PaginatedResponseSchema)
def carts(request,  page: int = Query(1), page_size: int = Query(10), user_id: int = None, purchased: bool = None ,ordering: str = None,):
    qs = Cart.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if user_id:
        qs = qs.filter(user__id=user_id)

    if purchased:
        qs = qs.filter(purchased=purchased)
    
    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, CartOutSchema, page_number, page_size)

# Read Single Cart (Retrieve)
@router.get("/carts/{cart_id}/", response=CartOutSchema)
def retrieve_cart(request, cart_id: int):
    cart = get_object_or_404(Cart, id=cart_id)
    return cart

# Update Cart
@router.put("/carts/{cart_id}/", response=CartOutSchema)
def update_cart(request, cart_id: int, payload: CartUpdateSchema):
    cart = get_object_or_404(Cart, id=cart_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(cart, attr, value)
    cart.save()
    return cart

# Delete Cart
@router.delete("/carts/{cart_id}/")
def delete_cart(request, cart_id: int):
    cart = get_object_or_404(Cart, id=cart_id)
    cart.delete()
    return {"success": True}




# Create CartItem
@router.post("/cart-items/", response=CartItemOutSchema)
def create_cart_item(request, payload: CartItemCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    cart_item = CartItem(**payload.dict())
        
    cart_item.save()
    return cart_item

# Read CartItems (List)
@router.get("/cart-items/", response=PaginatedResponseSchema)
def cart_items(request,  page: int = Query(1), page_size: int = Query(10), product_listing_id: int = None ,cart_id: int = None, ordering: str = None):
    qs = CartItem.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if product_listing_id:
        qs = qs.filter(product_listing__id=product_listing_id)

    if cart_id:
        qs = qs.filter(cart__id=cart_id)
    
    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, CartItemOutSchema, page_number, page_size)

# Read Single CartItem (Retrieve)
@router.get("/cart-items/{cart_item_id}/", response=CartItemOutSchema)
def retrieve_cart_item(request, cart_item_id: int):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    return cart_item

# Update CartItem
@router.put("/cart-items/{cart_item_id}/", response=CartItemOutSchema)
def update_cart_item(request, cart_item_id: int, payload: CartItemUpdateSchema):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(cart_item, attr, value)
    cart_item.save()
    return cart_item

# Delete CartItem
@router.delete("/cart-items/{cart_item_id}/")
def delete_cart_item(request, cart_item_id: int):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return {"success": True}



# Create Wishlist
@router.post("/wishlists/", response=WishlistOutSchema)
def create_wishlist(request, payload: WishlistCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    wishlist = Wishlist(**payload.dict())
        
    wishlist.save()
    return wishlist

# Read Wishlists (List)
@router.get("/wishlists/", response=PaginatedResponseSchema)
def wishlists(request,  page: int = Query(1), page_size: int = Query(10), user_id: int = None, ordering: str = None):
    qs = Wishlist.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if user_id:
        qs = qs.filter(user__id=user_id)
    
    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, WishlistOutSchema, page_number, page_size)

# Read Single Wishlist (Retrieve)
@router.get("/wishlists/{wishlist_id}/", response=WishlistOutSchema)
def retrieve_wishlist(request, wishlist_id: int):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)
    return wishlist

# Update Wishlist
@router.put("/wishlists/{wishlist_id}/", response=WishlistOutSchema)
def update_wishlist(request, wishlist_id: int, payload: WishlistUpdateSchema):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(wishlist, attr, value)
    wishlist.save()
    return wishlist

# Delete Wishlist
@router.delete("/wishlists/{wishlist_id}/")
def delete_wishlist(request, wishlist_id: int):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id)
    wishlist.delete()
    return {"success": True}



# Create WishlistItem
@router.post("/wishlist_items/", response=WishlistItemOutSchema)
def create_wishlist_item(request, payload: WishlistItemCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    wishlist_item = WishlistItem(**payload.dict())
        
    wishlist_item.save()
    return wishlist_item

# Read WishlistItems (List)
@router.get("/wishlist_items/", response=PaginatedResponseSchema)
def wishlist_items(request,  page: int = Query(1), page_size: int = Query(10), product_listing_id: int = None, wishlist_id: int = None, ordering: str = None):
    qs = WishlistItem.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if product_listing_id:
        qs = qs.filter(product_listing__id=product_listing_id)

    if wishlist_id:
        qs = qs.filter(wishlist__id=wishlist_id)
    
    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, WishlistItemOutSchema, page_number, page_size)

# Read Single WishlistItem (Retrieve)
@router.get("/wishlist_items/{wishlist_item_id}/", response=WishlistItemOutSchema)
def retrieve_wishlist_item(request, wishlist_item_id: int):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    return wishlist_item

# Update WishlistItem
@router.put("/wishlist_items/{wishlist_item_id}/", response=WishlistItemOutSchema)
def update_wishlist_item(request, wishlist_item_id: int, payload: WishlistItemUpdateSchema):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(wishlist_item, attr, value)
    wishlist_item.save()
    return wishlist_item

# Delete WishlistItem
@router.delete("/wishlist_items/{wishlist_item_id}/")
def delete_wishlist_item(request, wishlist_item_id: int):
    wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id)
    wishlist_item.delete()
    return {"success": True}
