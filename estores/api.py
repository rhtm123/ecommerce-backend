
from ninja import  Router, Query

# router.py
from .models import DeliveryPin
from .schemas import DeliveryPinOutSchema


from utils.pagination import PaginatedResponseSchema, paginate_queryset

router = Router()



@router.get("/delivery-pins/", response=PaginatedResponseSchema)
def deliverypins(request, 
           page: int = Query(1), 
           page_size: int = Query(10), 
           estore_id: int = None, 
           ordering: str = None, 
    ):

    qs = DeliveryPin.objects.all()

    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if estore_id:
        qs = qs.filter(estore__id=estore_id)
        query += f"&estore_id={estore_id}"

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    return paginate_queryset(request, qs, DeliveryPinOutSchema, page_number, page_size, query)
