
from ninja import  Router, Query

# router.py
from .models import Category, FeatureGroup, FeatureTemplate, Product, ProductListing, Feature
from .schemas import ( 
    CategoryCreateSchema, CategoryOutSchema, CategoryUpdateSchema,
    # CategoryFeatureValuesOutSchema,
    CategorySchema, CategoryParentChildrenOutSchema,
    FeatureGroupOutSchema,
    FeatureTemplateOutSchema,
    ProductCreateSchema, ProductOutSchema, ProductUpdateSchema,
    ProductListingUpdateSchema, ProductListingCreateSchema, ProductListingOutSchema, ProductListingOneOutSchema,
    FeatureOutSchema,
)
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset

import json 
from django.db.models import Min, Max, Count


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
def categories(request,  page: int = Query(1), page_size: int = Query(10), level: int = None):
    qs = Category.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if level:
        qs = qs.filter(level=level)

    return paginate_queryset(request, qs, CategoryOutSchema, page_number, page_size)

@router.get("/categories/parents_children/{category_id}/", response=CategoryParentChildrenOutSchema)
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


@router.get("/feature_groups/", response=PaginatedResponseSchema)
def featuregroups(request,  page: int = Query(1), page_size: int = Query(10), category_id:str = None , ordering: str = None,):
    qs = FeatureGroup.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if category_id:
        qs = qs.filter(category__id=category_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, FeatureGroupOutSchema , page_number, page_size)



@router.get("/feature_templates/", response=PaginatedResponseSchema)
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
@router.post("/products/", response=ProductOutSchema)
def create_product(request, payload: ProductCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)
    product = Product(**payload.dict())
        
    product.save()
    return product

# Read Products (List)
@router.get("/products/", response=PaginatedResponseSchema)
def products(request,  page: int = Query(1), page_size: int = Query(10), category_id:str = None , ordering: str = None,):
    qs = Product.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    if category_id:
        qs = qs.filter(category__id=category_id)

    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, ProductOutSchema, page_number, page_size)

# Read Single Product (Retrieve)
@router.get("/products/{product_id}/", response=ProductOutSchema)
def retrieve_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product

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


@router.post("/product_listings/", response=ProductListingOutSchema)
def create_product_listing(request, payload: ProductListingCreateSchema):

    product_listing = ProductListing(**payload.dict())
        
    product_listing.save()
    return product_listing

# Read ProductListings (List)
# /api/product_listings/?category_id=5&brand_ids=1&min_price=2000&feature_filters={"ram":["8GB"]}

@router.get("/product_listings/", response=PaginatedResponseSchema)
def product_listings(
    request,
    page: int = Query(1),
    page_size: int = Query(10),
    category_id: str = None,
    search: str = None,
    ordering: str = None,
    brand_ids: str = Query(None, description="Comma-separated brand IDs"),  # Example: '1,2,3'
    min_price: float = Query(None, description="Minimum price"),
    max_price: float = Query(None, description="Maximum price"),
    feature_filters: str = Query(None, description="Feature filters as JSON string"),  # Example: '{"1": ["4GB", "6GB"], "2": ["128GB"]}' ## 1 -> filter_template id
    ):
    qs = ProductListing.objects.all()

    # Filter by category
    if category_id:
        qs = qs.filter(category__id=category_id)

    if search: 
        qs = qs.filter(name__contains=search)

    # Filter by brands
    if brand_ids:
        brand_id_list = brand_ids.split(",")  # Split comma-separated string into list
        qs = qs.filter(brand__id__in=brand_id_list)

    # Filter by price range
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    # Filter by features
    if feature_filters:
        try:
            for feature_template_id, values in feature_filters.items():
                qs = qs.filter(
                    product_listing_features__feature_template__id=feature_template_id,
                    product_listing_features__value__in=values,
                )
        except Exception as e:
            return {"error": f"Feature filter error: {str(e)}"}

    # Ordering
    if ordering:
        qs = qs.order_by(ordering)

    # Paginate the results
    return paginate_queryset(request, qs, ProductListingOutSchema, page, page_size)



@router.get("/sidebar_filters/", tags=["Sidebar filters"])
def get_sidebar_filters(
    request, 
    category_id: str = None,
    brand_ids: str = Query(None, description="Comma-separated brand IDs"),  # Example: '1,2,3'
    min_price: float = Query(None, description="Minimum price"),
    max_price: float = Query(None, description="Maximum price"),
    feature_filters: str = Query(None, description="Feature filters as JSON string"),  # Example: '{"1": ["4GB", "6GB"], "2": ["128GB"]}'
    ):
    """
    API to fetch sidebar filters for product listings.
    """
    filters = {}
    
    # Filter listings by category if category_id is provided
    qs = ProductListing.objects.all()
    
    # Filter by category
    if category_id:
        qs = qs.filter(category__id=category_id)

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


# Read Single ProductListing (Retrieve)
@router.get("/product_listings/{product_listing_id}/", response=ProductListingOneOutSchema)
def retrieve_product_listing(request, product_listing_id: int):
    product_listing = get_object_or_404(ProductListing, id=product_listing_id)
    return product_listing

@router.get("/product_listings/slug/{product_listing_slug}/", response=ProductListingOneOutSchema)
def retrieve_product_listing_slug(request, product_listing_slug: str):
    product_listing = get_object_or_404(ProductListing, slug=product_listing_slug)
    return product_listing

# Update ProductListing
@router.put("/product_listings/{product_listing_id}/", response=ProductListingOutSchema)
def update_product_listing(request, product_listing_id: int, payload: ProductListingUpdateSchema):
    product_listing = get_object_or_404(ProductListing, id=product_listing_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(product_listing, attr, value)
    product_listing.save()
    return product_listing

# Delete ProductListing
@router.delete("/product_listings/{product_listing_id}/")
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
