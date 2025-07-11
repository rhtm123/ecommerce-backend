
from .models import Advertisement
from ninja import  Router, Query
from django.shortcuts import get_object_or_404
from .schemas import AdvertisementOutSchema
# from typing import List

from utils.cache import cache_response

router = Router()


from utils.pagination import PaginatedResponseSchema, paginate_queryset
from keys.auth import APIKeyAuth


@router.get("/advertisements", response=PaginatedResponseSchema , auth=APIKeyAuth())
@cache_response()
def advertisements(request, page: int = Query(1), page_size: int = Query(10), estore_id: int = None, ordering: str = None):
    qs = Advertisement.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""
    
    if estore_id:
        qs = qs.filter(estore__id = estore_id)
        query = query + "&estore_id=" + str(estore_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, AdvertisementOutSchema, page_number, page_size, query)
