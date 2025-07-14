# search/index.py
from products.models import ProductListing  
from products.models import Category
from users.models import Entity
from .client import client
from meilisearch.errors import MeilisearchApiError


def serialize_product_listing(listing):
    return {
        "id": listing.id,
        "name": listing.name,
        "slug": listing.slug,
        "brand": listing.brand.name if listing.brand else "",
        "category": listing.category.name if listing.category else "",
        "description": listing.product.description if listing.product else "",
        "price": float(listing.price),
         "estore_id": listing.estore.id if listing.estore else None,
        "featured": listing.featured,
        "rating": float(listing.rating or 0),
    }

def serialize_category(cat):
    return {
        "id": cat.id,
        "name": cat.name,
        "slug": cat.slug,
        "description": cat.description or "",
         "estore_id": cat.estore.id if cat.estore else None,
    }

def serialize_brand(entity):
    return {
        "id": entity.id,
        "name": entity.name,
        "slug": entity.name.lower().replace(" ", "-"),
        "details": entity.details or "",
        "estore_id": entity.user.estore.id if (entity.user and entity.user.estore) else None,

    }


def index_product_listings():
    
    listings = ProductListing.objects.filter(approved=True)
    # print(listings);
    data = [serialize_product_listing(p) for p in listings]

     # ✅ Create index with primary key
    try:
        client.create_index("product_listings", {"primaryKey": "id"})
    except MeilisearchApiError:
        # Index already exists
        pass

    index = client.index("product_listings")
    
    index.update_settings({
        "searchableAttributes": ["name", "brand", "category"],
        "displayedAttributes": ["id", "name", "slug", "brand", "category", "price"],
        "rankingRules": [
            "words", "typo", "proximity", "attribute", "exactness"
        ]
    })

    index.update_filterable_attributes(["estore_id", "brand", "category", "price", "featured"])
    index.update_sortable_attributes(["price", "rating"])


    print(data);

    task = index.add_documents(data)

    print("✅ Product listings indexed successfully.")

    index.wait_for_task(task.task_uid, timeout_in_ms=10000)


    status = client.get_task(task.task_uid)
    print("Indexing status:", status)
    



def index_categories():
    categories = Category.objects.filter(approved=True)
    data = [serialize_category(c) for c in categories]

    
    try:
        client.create_index("categories", {"primaryKey": "id"})
    except MeilisearchApiError:
        # Index already exists
        pass

    index = client.index("categories")
    

    index.update_settings({
        "searchableAttributes": ["name"],
        "displayedAttributes": ["id", "name", "slug"],
    })

    index.update_filterable_attributes(["estore_id"])

    index.add_documents(data)


def index_brands():
    brands = Entity.objects.filter(entity_type="brand")
    data = [serialize_brand(b) for b in brands]

    try:
        client.create_index("brands", {"primaryKey": "id"})
    except MeilisearchApiError:
        # Index already exists
        pass

    index = client.index("brands")


    index.update_settings({
        "searchableAttributes": ["name"],
        "displayedAttributes": ["id", "name", "slug"],
    })

    index.update_filterable_attributes(["estore_id"])


    index.add_documents(data)
