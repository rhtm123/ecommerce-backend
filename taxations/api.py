from ninja import Router, Query
from typing import List
from .models import TaxCategory
from .schemas import TaxCategoryOutSchema, TaxCategoryCreateSchema, TaxCategoryUpdateSchema
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset

router = Router()

@router.post("/tax-categories/", response=TaxCategoryOutSchema)
def create_tax_category(request, payload: TaxCategoryCreateSchema):
    tax_category = TaxCategory.objects.create(**payload.dict())
    return tax_category

@router.get("/tax-categories/", response=PaginatedResponseSchema)
def list_tax_categories(request, page: int = 1, page_size: int = 10):
    queryset = TaxCategory.objects.all()
    return paginate_queryset(request, queryset, TaxCategoryOutSchema, page, page_size)

@router.get("/tax-categories/{tax_category_id}/", response=TaxCategoryOutSchema)
def retrieve_tax_category(request, tax_category_id: int):
    tax_category = get_object_or_404(TaxCategory, id=tax_category_id)
    return tax_category

@router.put("/tax-categories/{tax_category_id}/", response=TaxCategoryOutSchema)
def update_tax_category(request, tax_category_id: int, payload: TaxCategoryUpdateSchema):
    tax_category = get_object_or_404(TaxCategory, id=tax_category_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(tax_category, attr, value)
    tax_category.save()
    return tax_category

@router.delete("/tax-categories/{tax_category_id}/", response={204: None})
def delete_tax_category(request, tax_category_id: int):
    tax_category = get_object_or_404(TaxCategory, id=tax_category_id)
    tax_category.delete()
    return 204, None
