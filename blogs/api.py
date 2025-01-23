
from .models import Blog
from ninja import  Router, Query
from django.shortcuts import get_object_or_404
from .schemas import BlogOutSchema
# from typing import List

router = Router()


from utils.pagination import PaginatedResponseSchema, paginate_queryset


@router.get("/blogs", response=PaginatedResponseSchema)
# @paginate(PageNumberPagination)
def blogs(request, page: int = Query(1), page_size: int = Query(10), category_id: int = None, tag_id: int = None):
    qs = Blog.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if category_id:
        qs = qs.filter(category__id = category_id)

    if tag_id:
        qs = qs.filter(tags__id = tag_id)

    return paginate_queryset(request, qs, BlogOutSchema, page_number, page_size)


@router.get("/blogs/{blog_id}", response=BlogOutSchema)
def blog(request, blog_id: int):
    page = get_object_or_404(Blog, id=blog_id)
    return page