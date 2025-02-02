from ninja import  Router, Query

# router.py
from .models import Order, OrderItem


from .schemas import (
    OrderCreateSchema, OrderOutSchema, OrderUpdateSchema,
    OrderItemCreateSchema, OrderItemUpdateSchema, OrderItemOutSchema,
    
)

from django.shortcuts import get_object_or_404

from django.db.models import Sum, Count, F, Avg


from utils.pagination import PaginatedResponseSchema, paginate_queryset

from ninja_jwt.authentication import JWTAuth

from datetime import datetime, timedelta


router = Router()


############## 1 city ###########################

######################## Order #######################



from datetime import datetime, timedelta
from django.db.models import Sum, Avg
from ninja import Router
from .models import OrderItem

router = Router()


from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count
from ninja import Router
from .models import OrderItem

router = Router()

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
def orders(request,  page: int = Query(1), page_size: int = Query(10), user_id: int = None, ordering: str = None):
    # qs = Order.objects.all()
    qs = Order.objects.prefetch_related("items")  # Fetch order items efficiently

    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if user_id:
        qs = qs.filter(user__id=user_id)
        query = query + "&user_id=" + str(user_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, OrderOutSchema, page_number, page_size, query)

# Read Single Order (Retrieve)
@router.get("/orders/{order_id}/", response=OrderOutSchema)
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
def order_items(request,  page: int = Query(1), page_size: int = Query(10), order_id: int = None, seller_id:int = None , status:str = None , ordering: str = None):
    qs = OrderItem.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""
    if order_id:
        qs = qs.filter(order__id=order_id)
        query = query + "&order_id=" + str(order_id)

    if status:
        qs = qs.filter(status=status)
        query = query + "&status=" + str(status)

    if seller_id:
        qs = qs.filter(product_listing__seller__id=seller_id)
        query = query + "&seller_id=" + str(seller_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, OrderItemOutSchema, page_number, page_size, query)

# Read Single OrderItem (Retrieve)
@router.get("/order_items/{order_item_id}/", response=OrderItemOutSchema)
def retrieve_order_item(request, order_item_id: int):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    return order_item

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