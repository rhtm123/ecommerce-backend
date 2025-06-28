from ninja import  Router, Query
from typing import List
from django.core.cache import cache


# router.py
from .models import Order, OrderItem, DeliveryPackage, PackageItem

from .schemas import (
    OrderCreateSchema, OrderOutSchema, OrderUpdateSchema, OrderOutOneSchema,
    OrderItemCreateSchema, OrderItemUpdateSchema, OrderItemOutSchema,
    OrderItemOutOneSchema,
    DeliveryPackageOutSchema,
    PackageItemOutSchema,
    # AppliedCouponSchema,
    # AppliedCouponCreateSchema
)

from django.shortcuts import get_object_or_404

from django.db.models import Sum, Count, F, Avg

from utils.pagination import PaginatedResponseSchema, paginate_queryset

from ninja_jwt.authentication import JWTAuth

from datetime import datetime, timedelta

router = Router()
from .schemas import OrderDeliveryStatusSchema

from utils.cache import cache_response



@router.get("/delivery-status/{order_number}", response=OrderDeliveryStatusSchema)
@cache_response()
def get_order_delivery_status(request, order_number: str):
    order = get_object_or_404(Order, order_number=order_number)
    
    # Fetch all packages associated with the order
    packages = order.packages.all()
    package_data = []
    for package in packages:
        package_items = package.package_items.all()
        package_item_data = [
            {
                "id": item.order_item.id,
                "product_listing": item.order_item.product_listing.name,
                "product_listing_name": item.order_item.product_listing.name,
                "product_slug": item.order_item.product_listing.slug,
                "product_main_image": item.order_item.product_listing.main_image.url if item.order_item.product_listing.main_image else None,
                "quantity": item.order_item.quantity,
                "status": item.order_item.status,
                "price": float(item.order_item.price),
                "mrp": float(item.order_item.mrp) if item.order_item.mrp else float(item.order_item.product_listing.mrp or item.order_item.price),
                "discount_amount": float(item.order_item.discount_amount) if item.order_item.discount_amount else None,
                "subtotal": float(item.order_item.subtotal),
                "created": item.order_item.created,
                "shipped_date": item.order_item.shipped_date,
            } for item in package_items]
        
        package_data.append({
            "tracking_number": package.tracking_number,
            "status": package.status,
            "product_listing_count": package.product_listing_count,
            "total_units": package.total_units,
            "delivery_out_date": package.delivery_out_date.isoformat() if package.delivery_out_date else None,
            "delivered_date": package.delivered_date.isoformat() if package.delivered_date else None,
            "package_items": package_item_data,
            "created": package.created
        })
    
    # Fetch items that are not in any package
    items_without_package = []
    for order_item in order.order_items.all():
        if not PackageItem.objects.filter(order_item=order_item).exists():
            items_without_package.append({
                "id": order_item.id,
                "product_listing": order_item.product_listing.name,
                "product_listing_name": order_item.product_listing.name,
                "product_slug": order_item.product_listing.slug,
                "product_main_image": order_item.product_listing.main_image.url if order_item.product_listing.main_image else None,
                "quantity": order_item.quantity,
                "status": order_item.status,
                "price": float(order_item.price),
                "mrp": float(order_item.product_listing.mrp) if order_item.product_listing and order_item.product_listing.mrp else float(order_item.price),
                "discount_amount": float(order_item.discount_amount) if order_item.discount_amount else None,
                "subtotal": float(order_item.subtotal),
                "created": order_item.created,
                "shipped_date": order_item.shipped_date,
                "cancel_requested": order_item.cancel_requested,
                "cancel_reason":order_item.cancel_reason,
                "cancel_approved": order_item.cancel_approved,
                "return_requested": order_item.return_requested,
                "return_reason": order_item.return_reason,
                "return_approved": order_item.return_approved
            })
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "user": order.user.email,
        "total_amount": float(order.total_amount),
        "total_discount": float(order.total_discount),
        "payment_status": order.payment_status,
        "packages": package_data,
        "items_without_package": items_without_package,
        "coupon": {
            "code": order.coupon.code,
            "discount_type": order.coupon.discount_type,
            "discount_value": float(order.coupon.discount_value),
            "coupon_type": order.coupon.coupon_type,
        } if order.coupon else None,
        "offer": {
            "name": order.offer.name,
            "offer_type": order.offer.offer_type,
            "offer_scope": order.offer.offer_scope,
            "get_discount_percent": float(order.offer.get_discount_percent),
        } if order.offer else None,
        "discount_amount_coupon": float(order.discount_amount_coupon) if order.discount_amount_coupon else 0,
        "discount_amount_offer": float(order.discount_amount_offer) if order.discount_amount_offer else 0,
    }

@router.get("/seller-analytics", tags=["Analytics"])
@cache_response()
def analytics(request, seller_id: int = None, period: str = "lifetime"):
    """API for seller analytics with optional time filtering (week/month/lifetime)"""

    qs = OrderItem.objects.all()

    # Ensure seller_id is filtered through product_listing
    if seller_id:
        qs = qs.filter(product_listing__seller_id=seller_id)

    # Handle time-based filtering
    if period != "lifetime":
        if period == "week":
            start_date = datetime.now() - timedelta(days=7)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
        else:
            return {"error": "Invalid period. Use 'week', 'month', or 'lifetime'."}

        qs = qs.filter(created__gte=start_date)

    # Aggregations
    total_items = qs.count()
    total_revenue = qs.aggregate(total_revenue=Sum("subtotal"))["total_revenue"] or 0
    total_orders = qs.values("order").distinct().count()  # Count unique orders

    print(total_orders)

    orders = (
        qs.values("order")
        .annotate(order_total=Sum("subtotal"))
        .aggregate(average_order_value=Avg("order_total"))
    )
    average_order_value = orders["average_order_value"] or 0

    return {
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "total_items": total_items,
        "total_revenue": total_revenue,
    }


@router.get("/seller-analytics/sales-breakdown", tags=["Analytics"])
@cache_response()
def sales_breakdown(request, period: str, seller_id: int = None):
    """API for daily sales breakdown over the last week or month
    period possible values > weekly, monthly
    """
     
    # Determine the date range
    if period == "weekly":
        days = 7
    elif period == "monthly":
        days = 30
    else:
        return {"error": "Invalid period. Use 'weekly' or 'monthly'."}

    start_date = datetime.now() - timedelta(days=days)

    qs = OrderItem.objects.filter(created__gte=start_date)

    # Ensure seller_id filtering
    if seller_id:
        qs = qs.filter(product_listing__seller_id=seller_id)

    # Aggregate daily sales: revenue + count
    daily_sales = (
        qs.values("created__date")
        .annotate(
            total_revenue=Sum("subtotal"),
            total_quantity=Sum("quantity"),
            total_orders=Count("order", distinct=True)
        )
        .order_by("created__date")
    )

    return {"period": period, "sales_breakdown": list(daily_sales)}









@router.post("/orders/", response=OrderOutSchema, auth=JWTAuth())
def create_order(request, payload: OrderCreateSchema):

    order = Order(**payload.dict())
    order.save()
    return order

# Read Orders (List)

@router.get("/orders/", response=PaginatedResponseSchema)
@cache_response()
def orders(request, 
           page: int = Query(1), 
           page_size: int = Query(10), 
           user_id: int = None, 
           ordering: str = None, 
           items_needed: bool = False
    ):

    qs = Order.objects.all()

    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if user_id:
        qs = qs.filter(user__id=user_id)
        query += f"&user_id={user_id}"

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    
    orders_data = []

    if items_needed:
        query += f"&items_needed={items_needed}"

    for order in qs:
        order_data = {
            "id": order.id,
            "order_number": order.order_number,
            "user_id": order.user_id,
            "total_amount": float(order.total_amount or 0),
            # "subtotal_amount": float(order.subtotal_amount or 0),
            "total_discount": float(order.total_discount or 0),
            "shipping_address_id": order.shipping_address_id,
            "payment_status": order.payment_status,
            "notes": order.notes,
            "created": order.created,
            "updated": order.updated,
            "product_listing_count": order.product_listing_count,
            "total_units": order.total_units,
            "coupon": {
                "code":order.coupon.code ,
                "discount_type":order.coupon.discount_type ,
                "discount_value":order.coupon.discount_value ,
                "coupon_type":order.coupon.coupon_type,
            } if order.coupon else None,
            "offer": {
                "name": order.offer.name ,
                "offer_type": order.offer.offer_type ,
                "get_discount_percent": order.offer.get_discount_percent,
            } if order.offer else None,
        }

        # Add applied coupons
        # applied_coupons = [{
        #     "id": coupon.id,
        #     "code": coupon.code,
        #     "discount_type": coupon.discount_type,
        #     "discount_value": float(coupon.discount_value or 0),
        #     "discount_amount": float(coupon.discount_amount or 0),
        #     "created": coupon.created,
        # } for coupon in order.applied_coupons.all()]
        # order_data["applied_coupons"] = applied_coupons

        if items_needed:
            order_items = order.order_items.all()
            items_data = []
            for item in order_items:
                item_data = {
                    "id": item.id,
                    "product_listing_id": item.product_listing_id,
                    "product_listing_name": item.product_listing.name,
                    "product_slug": item.product_listing.slug,
                    "product_main_image": item.product_listing.main_image.url if item.product_listing.main_image else None,
                    "quantity": item.quantity,
                    "status": item.status,
                    "price": float(item.price or 0),
                    "mrp": float(item.product_listing.mrp) if item.product_listing.mrp else float(item.product_listing.mrp or item.price),
                    "review_added": item.review_added or False,
                    # "original_price": float(item.original_price or 0),
                    "discount_amount": float(item.discount_amount or 0),
                    "subtotal": float(item.subtotal or 0),
                    "shipped_date": item.shipped_date,
                    "cancel_requested": item.cancel_requested,
                    "cancel_reason":item.cancel_reason,
                    "cancel_approved": item.cancel_approved,
                    "return_requested": item.return_requested,
                    "return_reason": item.return_reason,
                    "return_approved": item.return_approved
                }
                
                # Add applied offers
                # applied_offers = [{
                #     "id": offer.id,
                #     "offer_name": offer.offer_name,
                #     "offer_type": offer.offer_type,
                #     "discount_amount": float(offer.discount_amount or 0),
                #     "buy_quantity": offer.buy_quantity,
                #     "get_quantity": offer.get_quantity,
                #     "get_discount_percent": float(offer.get_discount_percent or 0),
                #     "created": offer.created,
                # } for offer in item.applied_offers.all()]
                # item_data["applied_offers"] = applied_offers
                
                items_data.append(item_data)
            order_data["items"] = items_data
            
        orders_data.append(order_data)


    return paginate_queryset(request, orders_data, OrderOutSchema, page_number, page_size, query)

# Read Single Order (Retrieve)
@router.get("/orders/{order_id}/", response=OrderOutOneSchema)
def retrieve_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    
    # Get all order items with their applied offers
    order_items = []
    for item in order.order_items.all():
        # applied_offers = [{
        #     "id": offer.id,
        #     "offer_name": offer.offer_name,
        #     "offer_type": offer.offer_type,
        #     "discount_amount": float(offer.discount_amount),
        #     "buy_quantity": offer.buy_quantity,
        #     "get_quantity": offer.get_quantity,
        #     "get_discount_percent": float(offer.get_discount_percent),
        #     "created": offer.created,
        # } for offer in item.applied_offers.all()]
        
        item_data = {
            "id": item.id,
            "product_listing_name": item.product_listing.name,
            "quantity": item.quantity,
            "status": item.status,
            "price": float(item.price),
            "mrp": float(item.product_listing.mrp) if item.product_listing.mrp else float(item.product_listing.mrp or item.price),
            "discount_amount": float(item.discount_amount),
            "subtotal": float(item.subtotal),
            "shipped_date": item.shipped_date,
            # "applied_offers": applied_offers
        }
        order_items.append(item_data)
    
    # Get applied coupons
    # applied_coupons = [{
    #     "id": coupon.id,
    #     "code": coupon.code,
    #     "discount_type": coupon.discount_type,
    #     "discount_value": float(coupon.discount_value),
    #     "discount_amount": float(coupon.discount_amount),
    #     "created": coupon.created,
    # } for coupon in order.applied_coupons.all()]
    
    return {
        "id": order.id,
        "user": {
            "id": order.user.id,
            "first_name": order.user.first_name,
            "last_name": order.user.last_name,
            "email": order.user.email,
            "mobile": order.user.mobile,
            "role": order.user.role,
            "created": order.user.created,
            "updated": order.user.updated,
        } if order.user else None,
        "order_number": order.order_number,
        "total_amount": float(order.total_amount),
        "subtotal_amount": float(order.total_amount), 
        "total_discount": float(order.total_discount),
        "shipping_address": {
            "id": order.shipping_address.id,
            "address": order.shipping_address.address,
            "name": order.shipping_address.name,
            "mobile": order.shipping_address.mobile,
            "is_default": order.shipping_address.is_default,
            "created": order.shipping_address.created,
            "updated": order.shipping_address.updated
        } if order.shipping_address else None,
        "payment_status": order.payment_status,
        "notes": order.notes,
        "created": order.created,
        "updated": order.updated,
        "items": order_items,
        # "applied_coupons": applied_coupons,
    }

# Update Order
@router.put("/orders/{order_id}/", response=OrderOutSchema)
def update_order(request, order_id: int, payload: OrderUpdateSchema):
    order = get_object_or_404(Order, id=order_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(order, attr, value)
    order.save()
    return order

# Delete Order
@router.delete("/orders/{order_id}/")
def delete_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return {"success": True}




# Create OrderItem
@router.post("/order-items/", response=OrderItemOutSchema, auth=JWTAuth())
def create_order_item(request, payload: OrderItemCreateSchema):
    
    order_item = OrderItem(**payload.dict())    
    order_item.save()
    return order_item

# Read OrderItems (List)

@router.get("/order-items/", response=PaginatedResponseSchema)
@cache_response()
def order_items(
    request,  
    page_number: int = Query(1), 
    page_size: int = Query(10), 
    order_id: int = None, 
    seller_id: int = None, 
    status: str = None, 
    ordering: str = None, 
    need_reviews: bool = False,
    need_order_user: bool = False,
):
    qs = OrderItem.objects.all()
    
    # Apply filters
    if order_id:
        qs = qs.filter(order__id=order_id)
    if status:
        qs = qs.filter(status=status)
    if seller_id:
        qs = qs.filter(product_listing__seller__id=seller_id)
    if ordering:
        qs = qs.order_by(ordering)

    # Build query string
    query = ""
    if order_id:
        query += f"&order_id={order_id}"
    if status:
        query += f"&status={status}"
    if seller_id:
        query += f"&seller_id={seller_id}"
    if ordering:
        query += f"&ordering={ordering}"

    # Process items
    order_items_data = []
    for item in qs:
        review = getattr(item, 'order_item_reviews', None)
        
        # Base order data
        order_data = {
            "id": item.order.id,
        }

        # Add user data if requested
        if need_order_user:
            order_data.update({
                "user_id": item.order.user.id,
                "user": {
                    "id": item.order.user.id,
                    "username": item.order.user.username,
                    "first_name": item.order.user.first_name,
                    "last_name": item.order.user.last_name,
                }
            })
        
        item_data = {
            "id": item.id,
            "order_id": item.order.id,
            "order": order_data,
            "product_listing": {
                "name": item.product_listing.name,
                "id": item.product_listing.id,
                "slug": item.product_listing.slug,
                "price": item.product_listing.price,
                "mrp": float(item.order_item.mrp) if item.order_item.mrp else float(item.order_item.product_listing.mrp or item.order_item.price),
                "cgst_rate": item.product_listing.tax_category.cgst_rate if item.product_listing.tax_category else None,
                "sgst_rate": item.product_listing.tax_category.sgst_rate if item.product_listing.tax_category else None,
                "igst_rate": item.product_listing.tax_category.igst_rate if item.product_listing.tax_category else None,
            },
            "quantity": item.quantity,
            "price": float(item.price or 0),
            "mrp": float(item.order_item.mrp) if item.order_item.mrp else float(item.order_item.product_listing.mrp or item.order_item.price),
            "subtotal": float(item.subtotal or 0),
            "status": item.status,
            "created": item.created,
            "updated": item.updated,
            "cancel_requested": item.cancel_requested,
            "cancel_reason":item.cancel_reason,
            "cancel_approved": item.cancel_approved,
            "return_requested": item.return_requested,
            "return_reason": item.return_reason,
            "return_approved": item.return_approved,
            "review": None
        }
            
        # Add review data if requested
        if need_reviews and review:
            item_data["review"] = {
                "id": review.id,
                "rating": review.rating,
                "title": review.title,
                "comment": review.comment,
                "created": review.created,
                "updated": review.updated
            }

        order_items_data.append(item_data)

    return paginate_queryset(request, order_items_data, OrderItemOutSchema, page_number, page_size, query)
     

# Read Single OrderItem (Retrieve)

@router.get("/order-items/{order_item_id}/", response=OrderItemOutOneSchema)
@cache_response()
def retrieve_order_item(request, order_item_id: int):
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Access the review safely
    review = getattr(order_item, 'order_item_reviews', None)

    return {
        "id": order_item.id,
        "order": {
            "id": order_item.order.id,
            "user_id": order_item.order.user.id,
        },
         "product_listing": {
                "name":order_item.product_listing.name,
                "id": order_item.product_listing.id,
                "slug":order_item.product_listing.slug,
                "price": order_item.product_listing.price,
                "mrp": float(order_item.order_item.mrp) if order_item.order_item.mrp else float(order_item.order_item.product_listing.mrp or order_item.order_item.price),
                "cgst_rate": order_item.product_listing.tax_category.cgst_rate if order_item.product_listing.tax_category else None,
                "sgst_rate": order_item.product_listing.tax_category.sgst_rate if order_item.product_listing.tax_category else None,
                "igst_rate": order_item.product_listing.tax_category.igst_rate if order_item.product_listing.tax_category else None,
        }, 
        "quantity": order_item.quantity,
        "price": float(order_item.price),
        "subtotal": float(order_item.subtotal),
        "status": order_item.status,
        "created": order_item.created,
        "updated": order_item.updated,
        "review": {
            "id": review.id,
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "created": review.created,
            "updated": review.updated
        } if review else None  # Include review only if it exists
    }


# Update OrderItem
@router.put("/order-items/{order_item_id}/", response=OrderItemOutSchema, auth=JWTAuth())
def update_order_item(request, order_item_id: int, payload: OrderItemUpdateSchema):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(order_item, attr, value)
    order_item.save()
    return order_item

# Delete OrderItem
@router.delete("/order-items/{order_item_id}/")
def delete_order_item(request, order_item_id: int):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.delete()
    return {"success": True}


#### delivery 





# Read Orders (List)
@router.get("/delivery-packages/", response=PaginatedResponseSchema)
@cache_response()
def delivery_packages(request,  page: int = Query(1), page_size: int = Query(10), order_id: int = None, ordering: str = None):
    # qs = Order.objects.all()
    qs = DeliveryPackage.objects.all()  # Fetch order items efficiently

    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if order_id:
        qs = qs.filter(order__id=order_id)
        query = query + "&order_id=" + str(order_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, DeliveryPackageOutSchema, page_number, page_size, query)

# Read Single Order (Retrieve)
@router.get("/delivery-packages/{package_id}/", response=DeliveryPackageOutSchema)
def retrieve_delivery_package(request, package_id: int):
    package = get_object_or_404(DeliveryPackage, id=package_id)
    return package





# Read Orders (List)
@router.get("/package-items/", response=PaginatedResponseSchema)
@cache_response()
def package_items(request,  page: int = Query(1), page_size: int = Query(10), package_id: int = None, ordering: str = None):
    # qs = Order.objects.all()
    qs = PackageItem.objects.all()  # Fetch order items efficiently

    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if package_id:
        qs = qs.filter(package__id=package_id)
        query = query + "&package_id=" + str(package_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, PackageItemOutSchema, page_number, page_size, query)

# Read Single Order (Retrieve)
@router.get("/package-items/{package_item_id}/", response=DeliveryPackageOutSchema)
def retrieve_package_item(request, package_item_id: int):
    package_item = get_object_or_404(PackageItem, id=package_item_id)
    return package_item

# Create AppliedCoupon
# @router.post("/applied-coupons/", response=AppliedCouponSchema, auth=JWTAuth())
# def create_applied_coupon(request, payload: AppliedCouponCreateSchema):
#     order = get_object_or_404(Order, id=payload.order_id)
    
#     applied_coupon = AppliedCoupon.objects.create(
#         order=order,
#         code=payload.coupon_code,
#         discount_type=payload.discount_type,
#         discount_value=payload.discount_value,
#         discount_amount=payload.discount_amount
#     )
    
#     # Update order totals after applying coupon
#     order.update_totals()
    
#     return applied_coupon