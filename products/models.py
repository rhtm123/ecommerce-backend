from django.db import models
from users.models import Entity

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from imagekit.models import ImageSpecField

from treebeard.mp_tree import MP_Node
from taxations.models import TaxCategory


class Category(MP_Node):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    level = models.PositiveIntegerField(default=1)  # Static field for level

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically update the level before saving
        self.level = self.get_depth()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name 

class FeatureGroup(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_feature_groups", null=True, blank=True)
    name = models.CharField(max_length=255)  # E.g., 'Specifications', 'Camera'

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class FeatureTemplate(models.Model):
    name = models.CharField(max_length=255)  # E.g., 'RAM', 'Storage'
    feature_group = models.ForeignKey(FeatureGroup, on_delete=models.CASCADE, related_name='feature_templates', null=True, blank=True)
    key_feature = models.BooleanField(default=False)
    possible_values = models.JSONField(null=True, blank=True)

    # { type: "categorical", values: ["2GB", "4GB", "6GB"], }

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    important_info = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_products')
    manufacturer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="manufacturer_products", null=True, blank=True)
    brand = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="brand_products", null=True, blank=True)

    tax_category = models.ForeignKey(TaxCategory, on_delete=models.SET_NULL, null=True,blank=True)

    country_of_origin = models.CharField(max_length=255, default="India")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    # discount

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = ProcessedImageField(
        upload_to="products/",
        processors=[ResizeToFill(1200, 1200)],  # Resize to 800x800 pixels
        format="JPEG",
        options={"quality": 85},  # Save with 85% quality
    )

    thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(240, 240)],
                                      format='JPEG',
                                      options={'quality': 60})
    
    is_main = models.BooleanField(default=False)  # Indicates the primary image
    alt_text = models.CharField(max_length=255, blank=True, null=True)  # SEO optimization
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {'Main' if self.is_main else 'Gallery'} Image"


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')
    name = models.CharField(max_length=255) # example "Red, 128GB"
    attributes = models.JSONField() # { "color": "Red", "storage": "128GB"}
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_listings', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category_listings', null=True, blank=True)

    box_items = models.TextField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    # features example -> {"general": [{"name":"ram", "value":"6gb"}, {'name':"storage, "value":"128gb"}], "camera": [{"name":"front camera", "value":"40mp"]} 
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
    
class ProductListingImage(models.Model):
    listing = models.ForeignKey(
        ProductListing, on_delete=models.CASCADE, related_name="images"
    )
    image = ProcessedImageField(
        upload_to="listings/",
        processors=[ResizeToFill(800, 800)],  # Resize to 800x800 pixels
        format="JPEG",
        options={"quality": 85},  # Save with 85% quality
    )

    thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(100, 50)],
                                      format='JPEG',
                                      options={'quality': 60})
    is_main = models.BooleanField(default=False)  # Primary image for the listing
    alt_text = models.CharField(max_length=255, blank=True, null=True)  # SEO optimization
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.listing.product.name} - {self.listing.seller.name} Listing Image"

    
class Feature(models.Model):
    listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='product_listing_features')
    feature_group = models.CharField(max_length=255)  # e.g., 'general', 'camera'
    name = models.CharField(max_length=255, db_index=True)     # e.g., 'ram'
    value = models.CharField(max_length=255, db_index=True)    # e.g., '6gb'

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
