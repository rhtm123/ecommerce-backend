
from ninja import  Router, Query

# router.py
from .models import DeliveryPin, WebPage, EStore
from .schemas import DeliveryPinOutSchema, EStoreOutSchema, WebPageOutSchema, ThemeOutSchema
from django.shortcuts import get_object_or_404


from utils.pagination import PaginatedResponseSchema, paginate_queryset
from utils.cache import cache_response


router = Router()


@router.get("estores", response=PaginatedResponseSchema)
# @cache_response()
def estores(request, 
           page: int = 1, 
           page_size: int = 10, 
           ordering: str = None,
           name: str = Query(None, description="Filter by store name"),
    ):

    qs = EStore.objects.all()

    query = ""

    if name:
        qs = qs.filter(name__icontains=name)
        query += f"&name={name}"

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    return paginate_queryset(request, qs, EStoreOutSchema, page, page_size, query)


@router.get("/theme/{estore_id}", response=ThemeOutSchema)
# @cache_response()
def estore_theme_detail(request, estore_id: int):
    estore = get_object_or_404(EStore, id=estore_id)
    return estore.theme


@router.get("/estores/{estore_id}", response=EStoreOutSchema)
# @cache_response()
def estore_detail(request, estore_id: int):
    obj = get_object_or_404(EStore, id=estore_id)
    return obj

@router.get("/web-pages", response=PaginatedResponseSchema)
# @cache_response()
def static_pages(request, 
           page: int = 1, 
           page_size: int = 10, 
           estore_id: int = None, 
           ordering: str = None,
           name: str = Query(None, description="Filter by static page name"),
    ):

    qs = WebPage.objects.all()

    query = ""
    if estore_id:
        qs = qs.filter(estore__id=estore_id)
        query += f"&estore_id={estore_id}"  

    if name:
        qs = qs.filter(name__icontains=name)
        query += f"&name={name}"   

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    return paginate_queryset(request, qs, WebPageOutSchema, page, page_size, query)  


@router.get("/web-pages/{static_page_id}", response=WebPageOutSchema)
# @cache_response()
def static_page_detail(request, static_page_id: int):
    obj = get_object_or_404(WebPage, id=static_page_id)
    return obj


@router.get("/delivery-pins/", response=PaginatedResponseSchema)
@cache_response()
def deliverypins(request, 
           page: int = 1, 
           page_size: int = 10, 
           estore_id: int = None, 
           pin_code: str = Query(None, description="Filter by pin code"),
           ordering: str = None, 
    ):

    qs = DeliveryPin.objects.all()



    query = ""

    if estore_id:
        qs = qs.filter(estore__id=estore_id)
        query += f"&estore_id={estore_id}"

    if pin_code:
        qs = qs.filter(pin_code=pin_code)
        query += f"&pin_code={pin_code}"

    if ordering:
        qs = qs.order_by(ordering)
        query += f"&ordering={ordering}"

    return paginate_queryset(request, qs, DeliveryPinOutSchema, page, page_size, query)
