from django.db import models
from users.models import Entity

from estores.models import EStore

# from imagekit.models import ProcessedImageField
# from imagekit.processors import ResizeToFill

# from imagekit.models import ImageSpecField

from treebeard.mp_tree import MP_Node
from taxations.models import TaxCategory

from django.template.defaultfilters import slugify

# from decouple import config
 
from cloudinary.models import CloudinaryField

# from taxations.models import TaxCategory

CATEGORY_TYPE_CHOICES = [
    ('product', 'Product'),
    ('blog', 'Blog'),
]


class Category(MP_Node):
    name = models.CharField(max_length=255, unique=True)
    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_categories")
    
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(default="", null=False, blank=True)
    
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        default='product',
        help_text='Specify if the category is for a product or a blog.'
    )
    
    image = CloudinaryField(
        "image",
        folder="kb/product_listings/",
        transformation={"width": 400, "height": 400, "crop": "fill"},
        blank=True,
        null=True,
    )

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
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

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

    def __str__(self):
        return self.name

    # { type: "categorical", values: ["2GB", "4GB", "6GB"], }
    # { "type": "range", "min": 1, "max": 64, "unit": "GB" }


    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    important_info = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(default=0,max_digits=10, decimal_places=2)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category_products', null=True, blank=True)
    brand = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="brand_products", null=True, blank=True)

    tax_category = models.ForeignKey(
        TaxCategory, 
        related_name="tax_category_products",
        on_delete=models.SET_NULL, null=True,blank=True
    )
    country_of_origin = models.CharField(max_length=255, default="India")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    # discount

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')
    name = models.CharField(max_length=255) # example "Red, 128GB"
    attributes = models.JSONField() # [ {'name':"color", "value":"Red", "real_value":"#ff0000"}, {'name':"storage", "value":"128GB", "real_value":"128"}]
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    def __str__(self):
        return self.name 



class ReturnExchangePolicy(models.Model):
    name = models.CharField(max_length=100, help_text="Policy name (e.g., '7-day return')")
    return_available = models.BooleanField(default=False)
    exchange_available = models.BooleanField(default=False)
    return_days = models.PositiveIntegerField(null=True, blank=True, help_text="Number of days allowed for return")
    exchange_days = models.PositiveIntegerField(null=True, blank=True, help_text="Number of days allowed for exchange")
    conditions = models.TextField(null=True, blank=True, help_text="Conditions for return/exchange")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Return: {self.return_days} days, Exchange: {self.exchange_days} days"
    

class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_listings', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category_product_listings', null=True, blank=True)
    brand = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="brand_product_listings", null=True, blank=True)
    manufacturer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="manufacturer_product_listings", null=True, blank=True)

    tax_category = models.ForeignKey(
        TaxCategory, 
        related_name="tax_category_product_listings",
        on_delete=models.SET_NULL, null=True,blank=True
    )

    return_exchange_policy = models.ForeignKey(
        ReturnExchangePolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_listings",
        help_text="Return and exchange policy for this product"
    )

    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_product_listings")

    slug = models.SlugField(default="", max_length=255, null=False, blank=True, db_index=True)

    box_items = models.TextField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    
    # features example -> {"general": [{"name":"ram", "value":"6gb"}, {'name':"storage, "value":"128gb"}], "camera": [{"name":"front camera", "value":"40mp"]} 

    approved = models.BooleanField(default=False, help_text="Product_listing will be shown on the website/app")
    featured = models.BooleanField(default=False)
    # listed = models.BooleanField(default=False)

    main_image = CloudinaryField(
        "image",
        folder="kb/product_listings/",
        transformation={"width": 1200, "height": 1200, "crop": "fill"},
        blank=True,
        null=True,
    )

    # features text // json
    variant = models.OneToOneField(Variant, on_delete=models.SET_NULL, related_name="variant_listing", null=True, blank=True)
    seller = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name='seller_listings', null=True, blank=True)
    packer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="packer_listings", null=True, blank=True)
    importer = models.ForeignKey(Entity, on_delete=models.SET_NULL, related_name="importer_listings", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    rating = models.DecimalField(default=0,max_digits=4, decimal_places=2, null=True, blank=True)

    review_count = models.IntegerField(default=0, null=True, blank=True)
    popularity = models.IntegerField(default=100)
    stock = models.PositiveIntegerField(default=0)

    buy_limit = models.PositiveIntegerField(default=10, help_text="Maximum limit for this product in an order")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ['-id']
    
    def save(self, *args, **kwargs):

        if self.product.category:
            self.category = self.product.category
        
        if self.product.tax_category:
            self.tax_category = self.product.tax_category

        if self.product.brand:
            self.brand = self.product.brand


        new_name = self.product.name
        if self.variant:
            new_name = new_name + " [" + self.variant.name + "]"

        self.slug = slugify(new_name) + "-" + str(self.id) + "nm"
        self.name = new_name

        # print(new_name)

        super(ProductListing, self).save(*args, **kwargs)

    def get_full_main_image_url(self):
        """
        Returns the full URL for the main image stored in Cloudinary.
        """
        if self.main_image:
            # Assuming Cloudinary's URL format (update accordingly if needed)
            # cloudinary_base_url = f"https://res.cloudinary.com/{config('CLN_CLOUD_NAME')}/image/upload/"
            return self.main_image.url
        return None

# quality: You can set this to a specific value (e.g., 80 for 80% quality) or use Cloudinary's automatic quality feature ("auto" or "auto:good", "auto:best", etc.).
    
class ProductListingImage(models.Model):
    product_listing = models.ForeignKey(
        ProductListing, on_delete=models.CASCADE, related_name="images"
    )
    image = CloudinaryField(
        "image",
        folder="kb/product_listings/",
        transformation={"width": 1200, "height": 1200, "crop": "fill", "quality": "auto:good"},
        blank=True,
        null=True,
    )

    alt_text = models.CharField(max_length=255, blank=True, null=True)  # SEO optimization
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_listing.product.name} - {self.product_listing.seller.name} Listing Image"
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    
class Feature(models.Model):
    product_listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='product_listing_features')
    feature_group = models.CharField(max_length=255)  # e.g., 'general', 'camera'
    feature_template = models.ForeignKey(FeatureTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='features', db_index=True)

    value = models.CharField(max_length=255, db_index=True)    # e.g., '6gb'

    slug = models.SlugField(default="", null=False, blank=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.feature_template.name + "-" +self.value

    def save(self, *args, **kwargs):

        self.slug = "kb" + str(self.id) + slugify(self.feature_template.name)
        super(Feature, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'
