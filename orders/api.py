from ninja import  Router, Query, Schema
from typing import List, Optional


# router.py
from .models import Order, OrderItem, DeliveryPackage, PackageItem


from .schemas import (
    OrderCreateSchema, OrderOutSchema, OrderUpdateSchema, OrderOutOneSchema,
    OrderItemCreateSchema, OrderItemUpdateSchema, OrderItemOutSchema,
    OrderItemOutOneSchema,
    DeliveryPackageOutSchema,
    PackageItemOutSchema, 

    
)

from django.shortcuts import get_object_or_404

from django.db.models import Sum, Count, F, Avg


from utils.pagination import PaginatedResponseSchema, paginate_queryset

from ninja_jwt.authentication import JWTAuth

from datetime import datetime, timedelta

router = Router()
from .schemas import OrderDeliveryStatusSchema


@router.get("/delivery-status/{order_number}", response=OrderDeliveryStatusSchema)
def get_order_delivery_status(request, order_number: int):
    order = get_object_or_404(Order, order_number=order_number)
    
    # Fetch all packages associated with the order
    packages = order.packages.all()
    package_data = []
    for package in packages:
        package_items = package.package_items.all()
        package_item_data = [{
            "order_item": {
                "product_listing": item.order_item.product_listing.name,
                "quantity": item.order_item.quantity,
                "status": item.order_item.status,
                "price": float(item.order_item.price),
                "subtotal": float(item.order_item.subtotal),
            },
            "quantity": item.quantity,
        } for item in package_items]
        
        package_data.append({
            "tracking_number": package.tracking_number,
            "status": package.status,
            "product_listing_count": package.product_listing_count,
            "total_units": package.total_units,
            "shipped_date": package.shipped_date.isoformat() if package.shipped_date else None,
            "delivered_date": package.delivered_date.isoformat() if package.delivered_date else None,
            "package_items": package_item_data,
        })
    
    # Fetch items that are not in any package
    items_without_package = []
    for order_item in order.order_items.all():
        if not PackageItem.objects.filter(order_item=order_item).exists():
            items_without_package.append({
                "product_listing": order_item.product_listing.name,
                "quantity": order_item.quantity,
                "status": order_item.status,
                "price": float(order_item.price),
                "subtotal": float(order_item.subtotal),
            })
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "user": order.user.username,
        "total_amount": float(order.total_amount),
        "payment_status": order.payment_status,
        "packages": package_data,
        "items_without_package": items_without_package,
    }

@router.get("/seller-analytics", tags=["Analytics"])
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









# Create Order
@router.post("/orders/", response=OrderOutSchema, auth=JWTAuth())
def create_order(request, payload: OrderCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    order = Order(**payload.dict())
        
    order.save()
    return order

# Read Orders (List)

@router.get("/orders/", response=PaginatedResponseSchema)
def orders(request, 
           page: int = Query(1), 
           page_size: int = Query(10), 
           user_id: int = None, 
           ordering: str = None, 
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

    return paginate_queryset(request, qs, OrderOutSchema, page_number, page_size, query, items_required=items_required)

# Read Single Order (Retrieve)
@router.get("/orders/{order_id}/", response=OrderOutOneSchema)
def retrieve_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    return order

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
@router.post("/order_items/", response=OrderItemOutSchema, auth=JWTAuth())
def create_order_item(request, payload: OrderItemCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    order_item = OrderItem(**payload.dict())
        
    order_item.save()
    return order_item

# Read OrderItems (List)

@router.get("/order_items/", response=PaginatedResponseSchema)
def order_items(
    request,  
    page: int = Query(1), 
    page_size: int = Query(10), 
    order_id: int = None, 
    seller_id: int = None, 
    status: str = None, 
    ordering: str = None, 
    need_reviews: bool = False,
):
    qs = OrderItem.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""
    if order_id:
        qs = qs.filter(order__id=order_id)
        query += f"&order_id={order_id}"

    if status:
        qs = qs.filter(status=status)
        query += f"&status={status}"

    if seller_id:
        qs = qs.filter(product_listing__seller__id=seller_id)
        query += f"&seller_id={seller_id}"

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    # Fetch data and add review details

    if need_reviews:
        order_items_data = []
        for item in qs:
            review = getattr(item, 'order_item_reviews', None)  # Access OneToOneField safely

            order_items_data.append({
                "id": item.id,
                "order_id": item.order.id,
                "product_listing": {
                    "name":item.product_listing.name,
                    "id": item.product_listing.id,
                    "slug":item.product_listing.slug,
                },
                "quantity": item.quantity,
                "price": float(item.price),
                "subtotal": float(item.subtotal),
                "status": item.status,
                "created": item.created,
                "updated": item.updated,
                "review": {
                    "id": review.id,
                    "rating": review.rating,
                    "title": review.title,
                    "comment": review.comment,
                    "created": review.created,
                    "updated": review.updated
                } if review else None  # Include review only if it exists
            })

        return paginate_queryset(request, order_items_data, OrderItemOutSchema, page_number, page_size, query)

    return paginate_queryset(request, qs, OrderItemOutSchema, page_number, page_size, query)
     

# Read Single OrderItem (Retrieve)

@router.get("/order_items/{order_item_id}/", response=OrderItemOutOneSchema)
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
@router.put("/order_items/{order_item_id}/", response=OrderItemOutSchema, auth=JWTAuth())
def update_order_item(request, order_item_id: int, payload: OrderItemUpdateSchema):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(order_item, attr, value)
    order_item.save()
    return order_item

# Delete OrderItem
@router.delete("/order_items/{order_item_id}/")
def delete_order_item(request, order_item_id: int):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.delete()
    return {"success": True}


#### delivery 





# Read Orders (List)
@router.get("/delivery-packages/", response=PaginatedResponseSchema)
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