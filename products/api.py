
from ninja import  Router, Query

# router.py
from .models import Category, Product, ProductListing
from .schemas import ( 
    CategoryCreateSchema, CategoryOutSchema, CategoryUpdateSchema,
    ProductCreateSchema, ProductOutSchema, ProductUpdateSchema,
    ProductListingUpdateSchema, ProductListingCreateSchema, ProductListingOutSchema
)
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset

router = Router()

############################ Category ############################
# Create Category
@router.post("/categories/", response=CategoryOutSchema)
def create_category(request, payload: CategoryCreateSchema):
    category = Category(**payload.dict())

    category.save()
    return category

# Read Users (List)
@router.get("/categories/", response=PaginatedResponseSchema)
def categories(request,  page: int = Query(1), page_size: int = Query(10)):
    qs = Category.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    return paginate_queryset(request, qs, CategoryOutSchema, page_number, page_size)

# Read Single User (Retrieve)
@router.get("/categories/{category_id}/", response=CategoryOutSchema)
def retrieve_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
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



############################ Product ############################
@router.post("/product/", response=ProductOutSchema)
def create_product(request, payload: ProductCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    product = Product(**payload.dict())
        
    product.save()
    return product

# Read Products (List)
@router.get("/product/", response=PaginatedResponseSchema)
def product(request,  page: int = Query(1), page_size: int = Query(10)):
    qs = Product.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    return paginate_queryset(request, qs, ProductOutSchema, page_number, page_size)

# Read Single Product (Retrieve)
@router.get("/product/{product_id}/", response=ProductOutSchema)
def retrieve_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product

# Update Product
@router.put("/product/{product_id}/", response=ProductOutSchema)
def update_product(request, product_id: int, payload: ProductUpdateSchema):
    product = get_object_or_404(Product, id=product_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(product, attr, value)
    product.save()
    return product

# Delete Product
@router.delete("/product/{product_id}/")
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}


############################ Product Listing ####################


@router.post("/product_listings/", response=ProductListingOutSchema)
def create_product_listing(request, payload: ProductListingCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)

    product_listing = ProductListing(**payload.dict())
        
    product_listing.save()
    return product_listing

# Read ProductListings (List)
@router.get("/product_listings/", response=PaginatedResponseSchema)
def product_listings(request,  page: int = Query(1), page_size: int = Query(10)):
    qs = ProductListing.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)

    return paginate_queryset(request, qs, ProductListingOutSchema, page_number, page_size)

# Read Single ProductListing (Retrieve)
@router.get("/product_listings/{product_listing_id}/", response=ProductListingOutSchema)
def retrieve_product_listing(request, product_listing_id: int):
    product_listing = get_object_or_404(ProductListing, id=product_listing_id)
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
