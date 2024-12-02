from django.db import models
from users.models import Entity

# Create your models here.
# image (ImageField): To visually represent categories.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subcategories', blank=True, null=True)
    feature_names = models.JSONField(null=True, blank=True)
# {"general": [{'name':"ram", key_feature:true}, {'name':"storage", key_feature:true}]}

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

# is_active (BooleanField): To manage product visibility.
# image (ImageField): To store product images.

class Product(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    important_info = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    manufacturer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="manufacturer_products", null=True, blank=True)
    brand = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="brand_products", null=True, blank=True)

    country_of_origin = models.CharField(max_length=255, default="India")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    # discount

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')
    name = models.CharField(max_length=255) # example "Red, 128GB"
    attributes = models.JSONField() # { "color": "Red", "storage": "128GB"}
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_listings', null=True, blank=True)
    box_items = models.TextField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    approved = models.BooleanField(default=False)

    listed = models.BooleanField(default=False)
    # features text // json
    variant = models.OneToOneField(Variant, on_delete=models.SET_NULL, related_name="variant_listing", null=True, blank=True)
    seller = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name='seller_listings', null=True, blank=True)
    packer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="packer_listings", null=True, blank=True)
    importer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="importer_listings", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.seller.name}"