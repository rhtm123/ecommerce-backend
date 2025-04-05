
from ninja import  Router, Query

# router.py
from .models import ProductListingImage, Category, FeatureGroup, FeatureTemplate, Product, ProductListing, Feature
from .schemas import ( 
    CategoryCreateSchema, CategoryOutSchema, CategoryUpdateSchema,
    # CategoryFeatureValuesOutSchema,
    CategorySchema, CategoryParentChildrenOutSchema,
    FeatureGroupOutSchema,
    FeatureTemplateOutSchema,
    ProductCreateSchema, ProductOutSchema, ProductOutOneSchema, ProductUpdateSchema,
    ProductListingUpdateSchema, ProductListingCreateSchema, ProductListingOutSchema, ProductListingOneOutSchema,
    FeatureOutSchema,
    ProductListingImageOutSchema
)
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset

import json 
from django.db.models import Min, Max, Count

from utils.cache import cache_response


from django.db.models import Q

from ninja_jwt.authentication import JWTAuth

from typing import Optional


router = Router()

############################ Category ############################
# Create Category

@router.post("/categories/", response=CategoryOutSchema)
def create_category(request, payload: CategoryCreateSchema):
    # category = Category(**payload.dict())
    data = payload

    # print(data);

    if data.parent_id:
        # Adding as a child category
        parent = get_object_or_404(Category, id=data.parent_id)
        category = parent.add_child(
            name=data.name,
            description=data.description,
            feature_names=data.feature_names,
        )
    else:
        # Adding as a root category
        category = Category.add_root(
            name=data.name,
            description=data.description,
            feature_names=data.feature_names,
        )
    
    category.save()
    return category

# Read Users (List)
@router.get("/categories/", response=PaginatedResponseSchema)
@cache_response()
def categories(
        request,
        page: int = Query(1, description="Page number"),
        page_size: int = Query(10, description="Number of items per page"),
        estore_id: Optional[int] = Query(None, description="Filter by EStore ID"),
        level: Optional[int] = Query(None, description="Filter by category level"),
        has_blogs: Optional[bool] = Query(None, description="Filter categories that have associated blogs"),
        category_type: Optional[str] = Query("product", description="Type of category"),
    ):
    qs = Category.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if estore_id is not None:
        qs = qs.filter(estore__id=estore_id)
        query = query + "&estore_id=" + str(estore_id)

    if level:
        qs = qs.filter(level=level)
        query = query + "&level=" + str(level)

    if category_type:
        qs = qs.filter(category_type=category_type)
        query = query + "&category_type=" + category_type

    if has_blogs:
        qs = qs.filter(category_blogs__isnull=False).distinct()
        query = query + "&has_blogs=" + str(has_blogs)

    return paginate_queryset(request, qs, CategoryOutSchema, page_number, page_size)

@router.get("/categories/parents-children/{category_id}/", response=CategoryParentChildrenOutSchema)
@cache_response()
def retrieve_category_parents_children(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)

    def get_all_parents(category):
        parents = []
        while category.get_parent():
            category = category.get_parent()
            parents.insert(0,category)
        return parents
    
    parents = get_all_parents(category)

    # Get the children categories
    children = category.get_children()

    return {
        "parents": [CategorySchema.from_orm(parent) for parent in parents],
        "children": [CategorySchema.from_orm(child) for child in children],
    }



# Read Single User (Retrieve)
@router.get("/categories/{category_id}/", response=CategoryOutSchema)
def retrieve_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    return category


@router.get("/categories/slug/{category_slug}/", response=CategoryOutSchema)
@cache_response()
def retrieve_category_slug(request, category_slug: str):
    category = get_object_or_404(Category, slug=category_slug)
    return category

# Update User
@router.put("/categories/{category_id}/", response=CategoryOutSchema)
def update_category(request, category_id: int, payload: CategoryUpdateSchema):
    category = get_object_or_404(Category, id=category_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(category, attr, value)
    category.save()
    return category

# Delete User
@router.delete("/categories/{category_id}/")
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return {"success": True}


@router.get("/feature-groups/", response=PaginatedResponseSchema)
def featuregroups(request,  page: int = Query(1), page_size: int = Query(10), category_id:str = None , ordering: str = None,):
    qs = FeatureGroup.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if category_id:
        qs = qs.filter(category__id=category_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, FeatureGroupOutSchema , page_number, page_size)



@router.get("/feature-templates/", response=PaginatedResponseSchema)
def featuretemplates(request,  page: int = Query(1), page_size: int = Query(10), feature_group_id:str = None , ordering: str = None,):
    qs = FeatureTemplate.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if feature_group_id:
        qs = qs.filter(feature_group__id=feature_group_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, FeatureTemplateOutSchema , page_number, page_size)

############################ Product ############################
@router.post("/products/", response=ProductOutSchema,  auth=JWTAuth())
def create_product(request, payload: ProductCreateSchema):
    # locality = get_object_or_404(Locality, id=payload.locality_id)
    product = Product(**payload.dict())
    product.save()
    return product

# Read Products (List)
@router.get("/products/", response=PaginatedResponseSchema)
@cache_response()
def products(request,  page: int = Query(1), page_size: int = Query(10), category_id:str = None , ordering: str = None,):
    qs = Product.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    query = ""

    if category_id:
        qs = qs.filter(category__id=category_id)
        query = query + "&category_id=" + category_id

    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + ordering

    return paginate_queryset(request, qs, ProductOutSchema, page_number, page_size, query)

# Read Single Product (Retrieve)
@router.get("/products/{product_id}/", response=ProductOutOneSchema)
def retrieve_product(request, product_id: int):
    # product = get_object_or_404(Product, id=product_id)

    product = Product.objects.prefetch_related('product_variants').get(id=product_id)

    return {
        'id': product.id,
        'name': product.name,
        'about': product.about,
        'description': product.description,
        'important_info': product.important_info,
        'base_price': product.base_price,
        'tax_category': product.tax_category_id if product.tax_category else None,
        'country_of_origin': product.country_of_origin,
        'created': product.created,
        'updated': product.updated,
        'variants': product.product_variants.all()  # Queryset of Variant instances
    }

# Update Product
@router.put("/products/{product_id}/", response=ProductOutSchema)
def update_product(request, product_id: int, payload: ProductUpdateSchema):
    product = get_object_or_404(Product, id=product_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(product, attr, value)
    product.save()
    return product

# Delete Product
@router.delete("/products/{product_id}/")
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}


############################ Product Listing ####################


@router.post("/product-listings/", response=ProductListingOutSchema)
def create_product_listing(request, payload: ProductListingCreateSchema):

    product_listing = ProductListing(**payload.dict())
        
    product_listing.save()
    return product_listing

# Read ProductListings (List)
# /api/product_listings/?category_id=5&brand_ids=1&min_price=2000&feature_filters={"ram":["8GB"]}



@router.get("/product-listings/", response=PaginatedResponseSchema)
@cache_response()
def product_listings(
    request,
    page: int = Query(1),
    page_size: int = Query(10),
    category_id: str = None,
    seller_id: int = None,
    product_id:int = None,
    search: str = None,
    ordering: str = None,
    featured: bool = None,
    brand_ids: str = Query(None, description="Comma-separated brand IDs"),
    min_price: int = Query(None, description="Minimum price"),
    max_price: int = Query(None, description="Maximum price"),
    feature_filters: str = Query(None, description="Feature filters as JSON string"),
):
    qs = ProductListing.objects.filter(approved=True)
    query = ""

    # print("Product",category_id, brand_ids, min_price, max_price, feature_filters)


    if seller_id:
        qs = qs.filter(seller__id=seller_id)
        query = query + "&seller_id=" + str(seller_id)

    if product_id:
        qs = qs.filter(product__id=product_id)
        query = query + "&product_id=" + str(product_id)

        
    # Filter by category and its children
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            children = category.get_children()
            descendants = Category.objects.filter(Q(id=category.id) | Q(id__in=children.values_list('id', flat=True)))
            qs = qs.filter(category__in=descendants)
            query = query + "&category_id=" + category_id
        except Category.DoesNotExist:
            return {"error": "Category not found"}
        
    if featured:
        qs = qs.filter(featured =featured)
        query = query + "&featured=" + str(featured)

    # Filter by search term
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(product__name__icontains=search))
        query = query + "&search=" + search

    # Filter by brands
    if brand_ids:
        brand_id_list = brand_ids.split(",")
        qs = qs.filter(brand__id__in=brand_id_list)
        query = query + "&brand_ids=" + brand_ids

    # Filter by price range
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
        query = query + "&min_price=" + str(min_price)

    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
        query = query + "&max_price=" + str(max_price)

    # Filter by features
    if feature_filters:
        query = query + "&feature_filters=" + feature_filters
        try:
            feature_filters = json.loads(feature_filters)  # Parse the JSON string
            for feature_template_id, values in feature_filters.items():
                qs = qs.filter(
                    product_listing_features__feature_template__id=feature_template_id,
                    product_listing_features__value__in=values,
                )
        except Exception as e:
            return {"error": f"Feature filter error: {str(e)}"}

    # Ordering
    if ordering:
        query = query + "&ordering=" + ordering
        qs = qs.order_by(ordering)

    # Paginate the results
    return paginate_queryset(request, qs, ProductListingOutSchema, page, page_size, query)


@router.get("/sidebar-filters/", tags=["Sidebar filters"])
@cache_response()
def get_sidebar_filters(
    request, 
    category_id: str = None,
    search: str = None,
    brand_ids: str = Query(None, description="Comma-separated brand IDs"),  # Example: '1,2,3'
    min_price: float = Query(None, description="Minimum price"),
    max_price: float = Query(None, description="Maximum price"),
    feature_filters: str = Query(None, description="Feature filters as JSON string"),  # Example: '{"1": ["4GB", "6GB"], "2": ["128GB"]}'
    ):
    """
    API to fetch sidebar filters for product listings.
    """
    filters = {}

    # print(category_id, brand_ids, min_price, max_price, feature_filters)
    
    # Filter listings by category if category_id is provided
    qs = ProductListing.objects.all()
    
    # Filter by category
    
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            children = category.get_children()
            descendants = Category.objects.filter(Q(id=category.id) | Q(id__in=children.values_list('id', flat=True)))
            qs = qs.filter(category__in=descendants)
        except Category.DoesNotExist:
            return {"error": "Category not found"}
        

    
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(product__name__icontains=search))


    # Filter by brands
    if brand_ids:
        brand_id_list = brand_ids.split(",")  # Split comma-separated string into list
        qs = qs.filter(brand__id__in=brand_id_list)

    # Filter by price range
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    if feature_filters:
        try:
            for feature_template_id, values in feature_filters.items():
                qs = qs.filter(
                    product_listing_features__feature_template__id=feature_template_id,
                    product_listing_features__value__in=values,
                )
        except Exception as e:
            return {"error": f"Feature filter error: {str(e)}"}

    # Get brand filters
    filters['brands'] = list(
        qs.values('brand__id', 'brand__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # filters['categories'] = list(
    #     qs.values('category__id', 'category__name')
    #     .annotate(count=Count('id'))
    #     .order_by('-count')
    # )

    filters['features'] = list(
        qs.values('product_listing_features__feature_template__id', 'product_listing_features__feature_template__name','product_listing_features__value')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # print(filters)
    
    # Get price range
    price_range = qs.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    filters['price_range'] = {
        "min_price": price_range.get('min_price', 0),
        "max_price": price_range.get('max_price', 0)
    }

    return filters

@router.get("/product-listings/related/{product_listing_id}/", response=PaginatedResponseSchema)
@cache_response()
def get_related_products(
    request,
    product_listing_id: int,
    page: int = Query(1),
    page_size: int = Query(10),
    ):
    """
    Get related products for a specific product listing based on category, brand, features, and price similarity.
    """
    # Get the original product listing
    product_listing = get_object_or_404(ProductListing, id=product_listing_id, approved=True)
    qs = ProductListing.objects.filter(approved=True).exclude(id=product_listing_id)

    # Base filters for related products
    related_filters = Q()

    # 1. Same category filter
    if product_listing.category:
        related_filters &= Q(category=product_listing.category)

    # 2. Same brand filter
    # if product_listing.brand:
    #     related_filters &= Q(brand=product_listing.brand)

    # 3. Similar price range (±50% of original price)
    price = float(product_listing.price)
    min_price = price * 0.5  # 50% below
    max_price = price * 1.5  # 50% above
    related_filters &= Q(price__gte=min_price) & Q(price__lte=max_price)

    # 4. Feature similarity
    # if product_listing.features:
    #     try:
    #         features = product_listing.features
    #         # Look for products with at least one matching feature
    #         feature_filters = Q()
    #         for category in features:
    #             for feature in features[category]:
    #                 feature_filters |= Q(features__contains={category: [feature]})
    #         related_filters &= feature_filters
    #     except Exception:
    #         pass

    # Apply all filters
    qs = qs.filter(related_filters)

    # Order by relevance
    # - Featured products first
    # - Higher rating
    # - Higher popularity
    qs = qs.order_by('-featured', '-rating', '-popularity')

    # Paginate the results
    return paginate_queryset(request, qs, ProductListingOutSchema, page, page_size)


# Read Single ProductListing (Retrieve)
@router.get("/product-listings/{product_listing_id}/", response=ProductListingOneOutSchema)
def retrieve_product_listing(request, product_listing_id: int):
    product_listing = get_object_or_404(ProductListing, id=product_listing_id)
    return product_listing

@router.get("/product-listings/slug/{product_listing_slug}/", response=ProductListingOneOutSchema)
@cache_response()
def retrieve_product_listing_slug(request, product_listing_slug: str):
    product_listing = get_object_or_404(ProductListing, slug=product_listing_slug)
    return product_listing

# Update ProductListing
@router.put("/product-listings/{product_listing_id}/", response=ProductListingOutSchema)
def update_product_listing(request, product_listing_id: int, payload: ProductListingUpdateSchema):
    product_listing = get_object_or_404(ProductListing, id=product_listing_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(product_listing, attr, value)
    product_listing.save()
    return product_listing

# Delete ProductListing
@router.delete("/product-listings/{product_listing_id}/")
def delete_product_listing(request, product_listing_id: int):
    product_listing = get_object_or_404(ProductListing, id=product_listing_id)
    product_listing.delete()
    return {"success": True}


@router.get("/features/", response=PaginatedResponseSchema)
def features(request,  page: int = Query(1), page_size: int = Query(10), product_listing_id: int = None , ordering: str = None,):
    qs = Feature.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if product_listing_id:
        qs = qs.filter(product_listing_id__id=product_listing_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, FeatureOutSchema, page_number, page_size)



@router.get("/product-listing-images/", response=PaginatedResponseSchema)
def product_listing_images(request,  page: int = Query(1), page_size: int = Query(10), product_listing_id: int = None , ordering: str = None,):
    qs = ProductListingImage.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)


    if product_listing_id:
        qs = qs.filter(product_listing_id__id=product_listing_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, ProductListingImageOutSchema, page_number, page_size)
