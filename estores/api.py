
from ninja import  Router, Query

# router.py
from .models import DeliveryPin
from .schemas import DeliveryPinOutSchema


from utils.pagination import PaginatedResponseSchema, paginate_queryset
from utils.cache import cache_response


router = Router()



@router.get("/delivery-pins/", response=PaginatedResponseSchema)
@cache_response()
def deliverypins(request, 
           page: int = 1, 
           page_size: int = 10, 
           estore_id: int = None, 
           ordering: str = None, 
    ):

    qs = DeliveryPin.objects.all()



    query = ""

    if estore_id:
        qs = qs.filter(estore__id=estore_id)
        query += f"&estore_id={estore_id}"

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    return paginate_queryset(request, qs, DeliveryPinOutSchema, page, page_size, query)
