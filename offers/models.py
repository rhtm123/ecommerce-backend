from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import ProductListing
from django.utils import timezone

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    COUPON_TYPE_CHOICES = [
        ('product', 'Product Specific'),
        ('cart', 'Cart Wide'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES)
    
    # For cart-wide coupons
    min_cart_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  # Total times this coupon can be used
    used_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)  # How many times a single user can use this
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        return True

class ProductCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='product_coupons')
    product = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='coupons')
    
    class Meta:
        unique_together = ('coupon', 'product')

class UserCouponUsage(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'coupon')

class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('buy_x_get_y', 'Buy X Get Y'),
        ('bundle', 'Bundle Offer'),
        ('discount', 'Direct Discount'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    
    # For Buy X Get Y offers
    buy_quantity = models.PositiveIntegerField(default=1)
    get_quantity = models.PositiveIntegerField(default=0)
    get_discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Common fields
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductOffer(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='product_offers')
    product = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='offers')
    
    # For bundle offers
    is_primary = models.BooleanField(default=False)  # Indicates if this is the main product in a bundle
    bundle_quantity = models.PositiveIntegerField(default=1)
    bundle_discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ('offer', 'product')
