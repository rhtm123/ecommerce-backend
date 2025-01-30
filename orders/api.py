from ninja import  Router, Query

# router.py
from .models import Order, OrderItem


from .schemas import (
    OrderCreateSchema, OrderOutSchema, OrderUpdateSchema,
    OrderItemCreateSchema, OrderItemUpdateSchema, OrderItemOutSchema,
    
)

from django.shortcuts import get_object_or_404

from utils.pagination import PaginatedResponseSchema, paginate_queryset

from ninja_jwt.authentication import JWTAuth


router = Router()


############## 1 city ###########################

######################## Order #######################


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
def order_items(request,  page: int = Query(1), page_size: int = Query(10), order_id: int = None, ordering: str = None):
    qs = OrderItem.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""
    if order_id:
        qs = qs.filter(order__id=order_id)
        query = query + "&order_id=" + str(order_id)

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
@router.put("/order_items/{order_item_id}/", response=OrderItemOutSchema)
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