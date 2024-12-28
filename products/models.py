from django.db import models
from users.models import Entity

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from imagekit.models import ImageSpecField

from treebeard.mp_tree import MP_Node
from taxations.models import TaxCategory

from django.template.defaultfilters import slugify



class Category(MP_Node):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(default="", null=False, blank=True)



    level = models.PositiveIntegerField(default=1)  # Static field for level

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically update the level before saving
        self.level = self.get_depth()

        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name 

class FeatureGroup(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_feature_groups", null=True, blank=True)
    name = models.CharField(max_length=255)  # E.g., 'Specifications', 'Camera'

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FeatureTemplate(models.Model):
    name = models.CharField(max_length=255)  # E.g., 'RAM', 'Storage'
    feature_group = models.ForeignKey(FeatureGroup, on_delete=models.CASCADE, related_name='feature_templates', null=True, blank=True)
    key_feature = models.BooleanField(default=False)
    possible_values = models.JSONField(null=True, blank=True)

    # { type: "categorical", values: ["2GB", "4GB", "6GB"], }
    # { "type": "range", "min": 1, "max": 64, "unit": "GB" }


    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    important_info = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    tax_category = models.ForeignKey(TaxCategory, on_delete=models.SET_NULL, null=True,blank=True)
    country_of_origin = models.CharField(max_length=255, default="India")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    # discount


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')
    name = models.CharField(max_length=255) # example "Red, 128GB"
    attributes = models.JSONField() # { "color": {"name":"Red", "value":"#ff0000"}, "storage": {"name":"128GB", "value":"128"}}
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_listings', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category_listings', null=True, blank=True)
    brand = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="brand_product_listings", null=True, blank=True)
    manufacturer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="manufacturer_product_listings", null=True, blank=True)


    slug = models.SlugField(default="", null=False, blank=True, db_index=True)

    box_items = models.TextField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    # features example -> {"general": [{"name":"ram", "value":"6gb"}, {'name':"storage, "value":"128gb"}], "camera": [{"name":"front camera", "value":"40mp"]} 
    approved = models.BooleanField(default=False)

    listed = models.BooleanField(default=False)

    main_image = ProcessedImageField(
        upload_to="kb/product_listings/",
        processors=[ResizeToFill(1200, 1200)],  # Resize to 800x800 pixels
        format="WEBP",
        options={"quality": 85},  # Save with 85% quality
        null=True, blank=True
    )

    thumbnail = ImageSpecField(source='main_image',
                                      processors=[ResizeToFill(360, 360)],
                                      format='WEBP',)

    # features text // json
    variant = models.OneToOneField(Variant, on_delete=models.SET_NULL, related_name="variant_listing", null=True, blank=True)
    seller = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name='seller_listings', null=True, blank=True)
    packer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="packer_listings", null=True, blank=True)
    importer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="importer_listings", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    popularity = models.IntegerField(default=100)

    stock = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name}"
    
    class Meta:
        ordering = ['-id']
    
    def save(self, *args, **kwargs):

        new_name = self.product.name
        if self.variant:
            new_name = new_name + " [" + self.variant.name + "]"

        self.slug = slugify(new_name) + "-" + str(self.id) + "kb"
        self.name = new_name

        super(ProductListing, self).save(*args, **kwargs)

    
class ProductListingImage(models.Model):
    listing = models.ForeignKey(
        ProductListing, on_delete=models.CASCADE, related_name="images"
    )
    image = ProcessedImageField(
        upload_to="kb/product_listings/",
        processors=[ResizeToFill(1200, 1200)],  # Resize to 800x800 pixels
        format="WEBP",
        options={"quality": 85},  # Save with 85% quality
    )

    alt_text = models.CharField(max_length=255, blank=True, null=True)  # SEO optimization
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.listing.product.name} - {self.listing.seller.name} Listing Image"

    
class Feature(models.Model):
    listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='product_listing_features')
    feature_group = models.CharField(max_length=255)  # e.g., 'general', 'camera'
    feature_template = models.ForeignKey(FeatureTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='features', db_index=True)

    value = models.CharField(max_length=255, db_index=True)    # e.g., '6gb'

    slug = models.SlugField(default="", null=False, blank=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        self.slug = slugify(self.name)
        super(Feature, self).save(*args, **kwargs)
