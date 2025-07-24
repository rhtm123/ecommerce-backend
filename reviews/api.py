
from ninja import  Router, Query

# router.py
from .models import Review
from .schemas import ( 
    ReviewCreateSchema, ReviewOutSchema, ReviewUpdateSchema
)
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset


from ninja_jwt.authentication import JWTAuth

from utils.cache import cache_response
from django.core.cache import cache


router = Router()



############################ Review ############################
@router.post("/reviews/", response=ReviewOutSchema, auth=JWTAuth())
def create_review(request, payload: ReviewCreateSchema):
    review = Review(**payload.dict())  
    review.save()

    if payload.order_item_id:
        cache_key = f"cache:/api/review/reviews/?*order_item_id={payload.order_item_id}*"
        cache.delete(cache_key)
    return review

# Read Reviews (List)
@router.get("/reviews/", response=PaginatedResponseSchema)
@cache_response()
def reviews(request,  page: int = 1, page_size: int = 10, product_listing_id:str = None, order_item_id:int =None , user_id:int=None ,ordering: str = None, estore_id: int = None, approved: bool = False):
    qs = Review.objects.all()


    query = ""
    if estore_id:
        qs = qs.filter(product_listing__estore__id = estore_id)
        query = query + "&estore_id=" + str(estore_id)

    if approved:
        qs = qs.filter(approved = approved)
        query = query + "&approved=" + str(approved)

    if user_id:
        qs = qs.filter(user__id = user_id)
        query = query + "&user_id=" + str(user_id)

    if product_listing_id:
        qs = qs.filter(product_listing__id=product_listing_id)
        query = query + "&product_listing_id=" + str(product_listing_id)

    if order_item_id:
        qs = qs.filter(order_item__id=order_item_id)
        query = query + "&order_item_id=" + str(order_item_id)

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering
    
    return paginate_queryset(request, qs, ReviewOutSchema, page, page_size, query)

# Read Single Review (Retrieve)
@router.get("/reviews/{review_id}/", response=ReviewOutSchema)
def retrieve_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    return review

# Read Single Review (Retrieve)
@router.get("/reviews/order-item/{order_item_id}/", response=ReviewOutSchema)
@cache_response()
def retrieve_review_by_order_item(request, order_item_id: int):
    review = get_object_or_404(Review, order_item__id=order_item_id)
    return review

# Update Review
@router.put("/reviews/{review_id}/", response=ReviewOutSchema, auth=JWTAuth())
def update_review(request, review_id: int, payload: ReviewUpdateSchema):
    review = get_object_or_404(Review, id=review_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(review, attr, value)
    review.save()
    return review

# Delete Review
@router.delete("/reviews/{review_id}/", auth=JWTAuth())
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return {"success": True}

