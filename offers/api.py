from typing import List
from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
# from django.db import transaction
from django.db.models import Q

from .models import Coupon, Offer, ProductOffer, UserCouponUsage
from .schemas import (
    CouponCreate, CouponUpdate, CouponOut,
    OfferCreate, OfferUpdate, OfferOut,
    ProductOfferCreate, ProductOfferOut,
    CouponValidationResponse, OfferValidationResponse,
    OfferValidationRequest
)
from products.models import ProductListing
from decimal import Decimal
from utils.cache import cache_response
router = Router()



# Coupon Endpoints
@router.post("/coupons", response=CouponOut, tags=["Coupons"])
def create_coupon(request, payload: CouponCreate):
    coupon = Coupon.objects.create(**payload.dict())
    return coupon

@router.get("/coupons", response=List[CouponOut], tags=["Coupons"])
@cache_response()
def list_coupons(request, is_active: bool = None):
    qs = Coupon.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs

@router.get("/coupons/{coupon_id}", response=CouponOut, tags=["Coupons"])
def get_coupon(request, coupon_id: int):
    return get_object_or_404(Coupon, id=coupon_id)

@router.put("/coupons/{coupon_id}", response=CouponOut, tags=["Coupons"])
def update_coupon(request, coupon_id: int, payload: CouponUpdate):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(coupon, attr, value)
    coupon.save()
    return coupon

@router.delete("/coupons/{coupon_id}", tags=["Coupons"])
def delete_coupon(request, coupon_id: int):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    return {"success": True}


# Offer Endpoints
@router.post("/offers", response=OfferOut, tags=["Offers"])
def create_offer(request, payload: OfferCreate):
    offer = Offer.objects.create(**payload.dict())
    return offer

@router.get("/offers", response=List[OfferOut], tags=["Offers"])
@cache_response()
def list_offers(request, is_active: bool = None):
    qs = Offer.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs

@router.get("/offers/{offer_id}", response=OfferOut, tags=["Offers"])
def get_offer(request, offer_id: int):
    return get_object_or_404(Offer, id=offer_id)

@router.put("/offers/{offer_id}", response=OfferOut, tags=["Offers"])
def update_offer(request, offer_id: int, payload: OfferUpdate):
    offer = get_object_or_404(Offer, id=offer_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(offer, attr, value)
    offer.save()
    return offer

@router.delete("/offers/{offer_id}", tags=["Offers"])
def delete_offer(request, offer_id: int):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.delete()
    return {"success": True}

# Product Offer Endpoints
@router.post("/product-offers", response=ProductOfferOut, tags=["Product Offers"])
def create_product_offer(request, payload: ProductOfferCreate):
    product_offer = ProductOffer.objects.create(**payload.dict())
    return product_offer

@router.get("/product-offers", response=List[ProductOfferOut], tags=["Product Offers"])
@cache_response()
def list_product_offers(request, product_id: int = None):
    qs = ProductOffer.objects.all()
    if product_id:
        qs = qs.filter(product_id=product_id)
    return qs

@router.delete("/product-offers/{product_offer_id}", tags=["Product Offers"])
def delete_product_offer(request, product_offer_id: int):
    product_offer = get_object_or_404(ProductOffer, id=product_offer_id)
    product_offer.delete()
    return {"success": True}

@router.get("/product-offers/{product_listing_id}/", response=List[OfferOut], tags=["Offers"])
@cache_response()
def get_product_offers(request, product_listing_id: int):
    """
    Get all active offers for a specific product listing.
    This includes:
    1. Product-specific offers directly linked to this product
    2. Cart-wide offers that could be applied when this product is in cart
    """
    try:
        # Get current time for offer validation
        now = timezone.now()
        
        # Get the product listing
        product_listing = get_object_or_404(ProductListing, id=product_listing_id)
        
        # Base query for active offers within valid time period
        base_query = Q(
            is_active=True,
            valid_from__lte=now,
            valid_until__gt=now
        )
        
        # Get product-specific offers for this product
        product_offers = Q(
            offer_scope='product',
            product_offers__product_id=product_listing_id
        )
        
        # Get cart-wide offers where product price meets minimum
        cart_offers = Q(
            offer_scope='cart',
            min_cart_value__lte=product_listing.price
        )
        
        # Combine queries and return offers
        offers = Offer.objects.filter(
            base_query & (product_offers | cart_offers)
        ).distinct()
        
        return offers
    except Exception as e:
        print(f"Error in get_product_offers: {str(e)}")
        return []

# Validation Endpoints
@router.get("/validate-coupon/{coupon_code}", response=CouponValidationResponse, tags=["Validation"])
@cache_response()
def validate_coupon(
    request, 
    coupon_code: str, 
    cart_value: float = 0,
    product_id: int = None
):
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        
        # Basic validation
        if not coupon.is_valid():
            return CouponValidationResponse(
                is_valid=False,
                message="Coupon is not valid or has expired",
                discount_amount=None,
                final_price=None
            )
        
        # Check user usage limit only if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_usage = UserCouponUsage.objects.filter(
                user=request.user,
                coupon=coupon
            ).first()
            
            if user_usage and user_usage.used_count >= coupon.per_user_limit:
                return CouponValidationResponse(
                    is_valid=False,
                    message="You have exceeded the usage limit for this coupon",
                    discount_amount=None,
                    final_price=None
                )
        
        # Cart-wide coupon validation
        if coupon.coupon_type == 'cart':
            if Decimal(str(cart_value)) < coupon.min_cart_value:
                return CouponValidationResponse(
                    is_valid=False,
                    message=f"Cart value must be at least {coupon.min_cart_value}",
                    discount_amount=None,
                    final_price=None
                )
            
            # Calculate discount
            cart_value_decimal = Decimal(str(cart_value))
            if coupon.discount_type == 'percentage':
                discount = cart_value_decimal * (coupon.discount_value / Decimal('100'))
                if coupon.max_discount_amount:
                    discount = min(discount, coupon.max_discount_amount)
            else:  # FIXED
                discount = coupon.discount_value
            
            final_price = cart_value_decimal - discount
            
            return CouponValidationResponse(
                is_valid=True,
                message="Coupon is valid",
                discount_amount=discount.quantize(Decimal('0.01')),
                final_price=final_price.quantize(Decimal('0.01'))
            )
        
        # Product-specific coupon validation
        
    except Coupon.DoesNotExist:
        return CouponValidationResponse(
            is_valid=False,
            message="Coupon not found",
            discount_amount=None,
            final_price=None
        )

@router.post("/validate-offer/{offer_id}", response=OfferValidationResponse, tags=["Validation"])
def validate_offer(
    request,
    offer_id: int,
    payload: OfferValidationRequest
):
    offer = get_object_or_404(Offer, id=offer_id)
    
    if not offer.is_active or timezone.now() < offer.valid_from or timezone.now() > offer.valid_until:
        return OfferValidationResponse(
            is_valid=False,
            message="Offer is not active or has expired"
        )
    
    # Get all products in the cart
    products = {p.id: p for p in ProductListing.objects.filter(id__in=payload.product_ids)}
    product_quantities = dict(zip(payload.product_ids, payload.quantities))
    
    # Calculate total cart value
    total_cart_value = sum(products[p_id].price * Decimal(str(product_quantities[p_id])) for p_id in payload.product_ids)
    
    # Handle cart-wide offers
    if offer.offer_scope == 'cart':
        if total_cart_value < offer.min_cart_value:
            return OfferValidationResponse(
                is_valid=False,
                message=f"Cart value must be at least {offer.min_cart_value}"
            )
        
        if offer.offer_type == 'discount':
            discount = total_cart_value * (Decimal(str(offer.get_discount_percent)) / Decimal('100'))
            if offer.max_discount_amount:
                discount = min(discount, offer.max_discount_amount)
                
            return OfferValidationResponse(
                is_valid=True,
                message="Cart-wide discount offer is valid",
                discount_amount=discount.quantize(Decimal('0.01')),
                final_price=(total_cart_value - discount).quantize(Decimal('0.01')),
                qualifying_products=payload.product_ids
            )
    
    # Handle product-specific offers
    elif offer.offer_scope == 'product':
        # Get all products that are part of this offer
        offer_products = ProductOffer.objects.filter(offer=offer)
        qualifying_products = []
        qualifying_total = Decimal('0')
        
        # Check each product in cart against offer products
        for product_id, quantity in product_quantities.items():
            if offer_products.filter(product_id=product_id).exists():
                qualifying_products.append(product_id)
                qualifying_total += products[product_id].price * Decimal(str(quantity))
        
        if not qualifying_products:
            return OfferValidationResponse(
                is_valid=False,
                message="No qualifying products found for this offer"
            )
            
        if offer.offer_type == 'discount':
            discount = qualifying_total * (Decimal(str(offer.get_discount_percent)) / Decimal('100'))
            return OfferValidationResponse(
                is_valid=True,
                message="Product-specific discount offer is valid",
                discount_amount=discount.quantize(Decimal('0.01')),
                final_price=(qualifying_total - discount).quantize(Decimal('0.01')),
                qualifying_products=qualifying_products
            )
            
        elif offer.offer_type == 'buy_x_get_y':
            total_qualifying_quantity = sum(product_quantities[p_id] for p_id in qualifying_products)
            sets = int(total_qualifying_quantity // Decimal(str(offer.buy_quantity)))
            
            if sets == 0:
                return OfferValidationResponse(
                    is_valid=False,
                    message=f"Need to buy at least {offer.buy_quantity} qualifying items"
                )
            
            discount_items = min(Decimal(str(sets * offer.get_quantity)), total_qualifying_quantity)
            discount = (Decimal(str(offer.get_discount_percent)) / Decimal('100')) * qualifying_total * (discount_items / total_qualifying_quantity)
            
            return OfferValidationResponse(
                is_valid=True,
                message=f"Buy X Get Y offer applies to {int(discount_items)} items",
                discount_amount=discount.quantize(Decimal('0.01')),
                final_price=(qualifying_total - discount).quantize(Decimal('0.01')),
                qualifying_products=qualifying_products
            )
            
        elif offer.offer_type == 'bundle':
            bundle_products = list(offer_products)
            primary_products = [bp for bp in bundle_products if bp.is_primary]
            
            if not primary_products:
                return OfferValidationResponse(
                    is_valid=False,
                    message="Invalid bundle configuration"
                )
            
            # Check if all required products are in cart with correct quantities
            missing_products = []
            for bp in bundle_products:
                if bp.product_id not in product_quantities:
                    missing_products.append(bp.product_id)
                elif product_quantities[bp.product_id] < bp.bundle_quantity:
                    missing_products.append(bp.product_id)
            
            if missing_products:
                return OfferValidationResponse(
                    is_valid=False,
                    message=f"Missing or insufficient quantity for bundle products"
                )
            
            bundle_total = sum(products[bp.product_id].price * Decimal(str(bp.bundle_quantity))
                             for bp in bundle_products)
            discount = bundle_total * (Decimal(str(primary_products[0].bundle_discount_percent)) / Decimal('100'))
            
            return OfferValidationResponse(
                is_valid=True,
                message="Bundle offer is valid",
                discount_amount=discount.quantize(Decimal('0.01')),
                final_price=(bundle_total - discount).quantize(Decimal('0.01')),
                qualifying_products=[bp.product_id for bp in bundle_products]
            )
    
    return OfferValidationResponse(
        is_valid=False,
        message=f"Unknown offer type: {offer.offer_type}"
    )