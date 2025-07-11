from elasticsearch_dsl.query import MultiMatch
from django_elasticsearch_dsl.search import Search
from .documents import ProductListingDocument
from ninja import Router

router = Router()

@router.get("/elastic-search")
def search_products(request, q: str):
    search = ProductListingDocument.search().query(
        MultiMatch(query=q, fields=['name', 'slug', 'brand.name', 'category.name'])
    )
    results = search[:10].execute()
    return [
        {
            "id": hit.id,
            "name": hit.name,
            "slug": hit.slug,
            "price": hit.price,
            "brand": hit.brand.name if hit.brand else None,
            "category": hit.category.name if hit.category else None,
        }
        for hit in results
    ]
