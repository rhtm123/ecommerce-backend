
from .models import Blog, Tag
from ninja import  Router, Query
from django.shortcuts import get_object_or_404
from .schemas import BlogOutSchema, TagOutSchema
# from typing import List

router = Router()


from utils.pagination import PaginatedResponseSchema, paginate_queryset



@router.get("/tags", response=PaginatedResponseSchema)
# @paginate(PageNumberPagination)
def tags(request, page: int = Query(1), page_size: int = Query(10), estore_id: int = None, ordering: str = None):
    qs = Tag.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""
    
    if estore_id:
        qs = qs.filter(estore__id = estore_id)
        query = query + "&estore_id=" + str(estore_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, TagOutSchema, page_number, page_size, query)


@router.get("/tags/{tag_id}", response=TagOutSchema)
def tag(request, tag_id: int):
    page = get_object_or_404(Tag, id=tag_id)
    return page

@router.get("/tags/slug/{tag_slug}", response=TagOutSchema)
def tag(request, tag_slug: str):
    page = get_object_or_404(Tag, slug=tag_slug)
    return page



@router.get("/blogs", response=PaginatedResponseSchema)
# @paginate(PageNumberPagination)
def blogs(request, page: int = Query(1), page_size: int = Query(10), category_id: int = None, tag_id: int = None, estore_id: int = None):
    qs = Blog.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    query = ""
    if category_id:
        qs = qs.filter(category__id = category_id)
        query = query + "&category_id=" + str(category_id)

    if tag_id:
        qs = qs.filter(tags__id = tag_id)
        query = query + "&tag_id=" + str(tag_id)

    if estore_id:
        pass

    return paginate_queryset(request, qs, BlogOutSchema, page_number, page_size, query)


@router.get("/blogs/{blog_id}", response=BlogOutSchema)
def blog(request, blog_id: int):
    page = get_object_or_404(Blog, id=blog_id)
    return page

@router.get("/blogs/slug/{blog_slug}", response=BlogOutSchema)
def blog(request, blog_slug: str):
    page = get_object_or_404(Blog, slug=blog_slug)
    return page