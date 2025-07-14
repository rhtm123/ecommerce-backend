
from ninja import Router
router = Router()

from .client import client

router = Router()

@router.get("/products")
def search_products(request, 
        q: str, 
        estore_id: int, 
        brand: str = None,
        min_price: int = None,
        max_price: int = None,
        limit: int = 10,            
    ):
    filter_query = f"estore_id = {estore_id}"
    if brand:
        filter_query += f' AND brand = "{brand}"'
    if min_price and max_price:
        filter_query += f" AND price >= {min_price} AND price <= {max_price}"
        
    result = client.index("product_listings").search(
        q,
        {
            "filter": f"estore_id = {estore_id}",
            "limit": limit,
            "facets": ["brand", "category"],
            "sort": ["price:asc"]
        }
    )
    return result

## autocomplete 
@router.get("/autocomplete/products")
def autocomplete_products(request, q: str, estore_id: int, limit: int = 5):
    result = client.index("product_listings").search(
        q,
        {
            "filter": f"estore_id = {estore_id}",
            "limit": limit,
            "attributesToHighlight": ["name"]
        }
    )
    return [hit["name"] for hit in result["hits"]]


@router.get("/categories")
def search_categories(request, q: str, estore_id: int):
    result = client.index("categories").search(q, 
        {
            "filter": f"estore_id = {estore_id}",
            "limit": 10
        }                                           
    )
    return result["hits"]

### autocomplete 

@router.get("/autocomplete/brands")
def autocomplete_brands(request, q: str, estore_id: int, limit: int = 5):
    result = client.index("brands").search(
        q,
        {
            "filter": f"estore_id = {estore_id}",
            "limit": limit,
            "attributesToHighlight": ["name"]
        }
    )
    return [hit["name"] for hit in result["hits"]]



@router.get("/brands")
def search_brands(request, q: str, estore_id: int):
    result = client.index("brands").search(q,
        {
            "filter": f"estore_id = {estore_id}",
            "limit": 10
        }
    )
    return result["hits"]

## autocomplete 

@router.get("/autocomplete/categories")
def autocomplete_categories(request, q: str, estore_id: int, limit: int = 5):
    result = client.index("categories").search(
        q,
        {
            "filter": f"estore_id = {estore_id}",
            "limit": limit,
            "attributesToHighlight": ["name"]
        }
    )
    return [hit["name"] for hit in result["hits"]]


