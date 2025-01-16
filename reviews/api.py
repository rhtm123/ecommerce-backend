
from ninja import  Router, Query

# router.py
from .models import Review
from .schemas import ( 
    ReviewCreateSchema, ReviewOutSchema, ReviewUpdateSchema
)
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset



router = Router()



############################ Review ############################
@router.post("/reviews/", response=ReviewOutSchema)
def create_review(request, payload: ReviewCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)
    review = Review(**payload.dict())
        
    review.save()
    return review

# Read Reviews (List)
@router.get("/reviews/", response=PaginatedResponseSchema)
def reviews(request,  page: int = Query(1), page_size: int = Query(10), product_listing_id:str = None , ordering: str = None,):
    qs = Review.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if product_listing_id:
        qs = qs.filter(product_listing__id=product_listing_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, ReviewOutSchema, page_number, page_size)

# Read Single Review (Retrieve)
@router.get("/reviews/{review_id}/", response=ReviewOutSchema)
def retrieve_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    return review

# Update Review
@router.put("/reviews/{review_id}/", response=ReviewOutSchema)
def update_review(request, review_id: int, payload: ReviewUpdateSchema):
    review = get_object_or_404(Review, id=review_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(review, attr, value)
    review.save()
    return review

# Delete Review
@router.delete("/reviews/{review_id}/")
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return {"success": True}

