
from ninja import Router
router = Router()
from typing import List, Optional


from .client import client

router = Router()


@router.get("/products")
def search_products(
    request,
    q: str,
    estore_id: int,
    brand_ids: Optional[str] = None, # comma seperated values example 2,3,4
    category_id: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    limit: int = 10,
    ):
    filter_parts = [f"estore_id = {estore_id}"]

    # print(brand_ids)

    if brand_ids:
        brand_id_list = [id.strip() for id in brand_ids.split(",") if id.strip().isdigit()]
        if brand_id_list:
            filter_parts.append(f"brand_id IN [{', '.join(brand_id_list)}]")

    if category_id:
        filter_parts.append(f"category_id = {category_id}")

    if min_price is not None and max_price is not None:
        filter_parts.append(f"price >= {min_price} AND price <= {max_price}")

    filter_query = " AND ".join(filter_parts)

    result = client.index("product_listings").search(
        q,
        {
            "filter": filter_query,
            "limit": limit,
            "facets": ["brand", "category"]
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


