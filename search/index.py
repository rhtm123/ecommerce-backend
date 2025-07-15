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
        "brand_id": listing.brand.id if listing.brand else "",
        "category": listing.category.name if listing.category else "",
        "category_id": listing.category.id if listing.category else "",
        "description": listing.product.description if listing.product else "",
        "price": float(listing.price),
        "mrp": float(listing.mrp),
        "estore_id": listing.estore.id if listing.estore else None,
        "featured": listing.featured,
        "rating": float(listing.rating or 0),
        "main_image": listing.main_image.url if listing.main_image else None
    }

def serialize_category(cat):
    return {
        "id": cat.id,
        "name": cat.name,
        "slug": cat.slug,
        "description": cat.description or "",
        "estore_id": cat.estore.id if cat.estore else None,
        "image": cat.image.url if cat.image else None
    }

def serialize_brand(entity):
    return {
        "id": entity.id,
        "name": entity.name,
        "slug": entity.name.lower().replace(" ", "-"),
        "details": entity.details or "",
        "estore_id": entity.estore.id if (entity.estore) else None,
        "logo": entity.logo.url if entity.logo else None,

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
        "displayedAttributes": ["id", "name", "slug", "brand", "category", "price", "main_image", "mrp"],
        "rankingRules": [
            "words", "typo", "proximity", "attribute", "exactness"
        ]
    })

    index.update_filterable_attributes(["estore_id", "brand_id", "brand" , "category" ,"category_id", "price", "featured"])
    index.update_sortable_attributes(["price", "rating"])

    task = index.add_documents(data)



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
        "displayedAttributes": ["id", "name", "slug", "estore_id", "image"],
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
        "displayedAttributes": ["id", "name", "slug", "estore_id", "logo"],
    })

    index.update_filterable_attributes(["estore_id"])


    index.add_documents(data)
