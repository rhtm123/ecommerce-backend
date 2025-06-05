from django.db import models
from users.models import ShippingAddress
from products.models import ProductListing

from django.conf import settings
# from users.models import Entity

from estores.models import EStore

# from django.core.exceptions import ValidationError

from utils.generate import generate_tracking_number, generate_order_number

# import datetime
from django.core.cache import cache

from django.utils import timezone

from offers.models import Coupon, Offer


PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
)

class Order(models.Model):

    estore = models.ForeignKey(EStore, on_delete=models.SET_NULL, null=True, blank=True, related_name="estore_orders")

    order_number = models.CharField(max_length=24, null=True,blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True , blank=True, related_name='orders')
    # status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price of all items including taxes and discounts")
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default='pending', choices=PAYMENT_CHOICES)
    # tracking_number = models.CharField(max_length=255, blank=True, null=True)

    # total_items = models.PositiveIntegerField(default=1, null=True, blank=True, help_text="No. of product listings (items)")
    notes = models.TextField(blank=True, null=True)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

        # Applied Coupon 
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True,)
    discount_amount_coupon = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Actual discount amount applied

    # Applied Offer

    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount_offer = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Actual discount amount applied


    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    product_listing_count = models.PositiveIntegerField(default=0)
    total_units = models.PositiveIntegerField(default=0)


    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()

        if self.user:
            cache_key = f"cache:/api/order/orders/?items_needed=true&user_id={self.user.id}&ordering=-id"
            cache.delete(cache_key)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    @property
    def subtotal_amount(self):
        """Calculate the subtotal amount before any discounts"""
        return sum(item.quantity * item.price for item in self.order_items.all())

    def update_totals(self):
        # Update product listing count and total units
        self.product_listing_count = self.order_items.count()
        self.total_units = sum(item.quantity for item in self.order_items.all())
        
        # Calculate subtotal (before discounts)
        self.total_amount = sum(item.quantity * item.price for item in self.order_items.all())
        
        # Initialize discount amounts
        self.discount_amount_coupon = 0
        self.discount_amount_offer = 0
        
        # Calculate offer discounts from OrderItems
        self.discount_amount_offer = sum(item.discount_amount for item in self.order_items.all())
        
        # Calculate coupon discount if a valid coupon is applied
        if self.coupon and self.coupon.is_valid():
            print("applying coupon")
            if self.coupon.coupon_type == 'cart':
                # Cart-wide coupon
                if self.subtotal_amount >= self.coupon.min_cart_value:
                    if self.coupon.discount_type == 'percentage':
                        discount = (self.coupon.discount_value / 100) * self.subtotal_amount
                        if self.coupon.max_discount_amount:
                            discount = min(discount, self.coupon.max_discount_amount)
                        self.discount_amount_coupon = discount
                    else:  # fixed
                        self.discount_amount_coupon = min(self.coupon.discount_value, self.subtotal_amount)

        # Calculate offer discount if a valid offer is applied
        if self.offer and self.offer.is_active:
            if self.offer.offer_type == 'buy_x_get_y':
                for item in self.order_items.all():
                    eligible_sets = item.quantity // self.offer.buy_quantity
                    free_items = eligible_sets * self.offer.get_quantity
                    if self.offer.get_discount_percent > 0:
                        discount = (self.offer.get_discount_percent / 100) * (item.price * free_items)
                        self.discount_amount_offer += discount
            elif self.offer.offer_type == 'bundle':
                # Bundle offer logic (assumes specific products are bundled)
                # You may need to verify if order_items match bundle requirements
                pass  # Implement based on your bundle logic
            elif self.offer.offer_type == 'discount':
                # Direct discount logic
                for item in self.order_items.all():
                    # Assuming offer applies to specific products
                    self.discount_amount_offer += (self.offer.get_discount_percent / 100) * (item.price * item.quantity)
            
        # Calculate total discount
        self.discount_amount_coupon = round(self.discount_amount_coupon)
        self.discount_amount_offer = round(self.discount_amount_offer)

        self.total_discount = self.discount_amount_coupon + self.discount_amount_offer
        
        # Calculate final total amount
        # self.total_amount = max(self.subtotal_amount - self.total_discount, Decimal('0.00'))
        
        # Save the updated fields
        self.save(update_fields=[
            'product_listing_count',
            'total_units',
            'discount_amount_coupon',
            'discount_amount_offer',
            'total_discount',
            'total_amount'
        ])


    def get_latest_payment(self):
        return self.payments.order_by('-created').first()


STATUS_CHOICES = [
    ('order_placed', 'order_placed'),
    ('shipped', 'shipped'),
    ('ready_for_delivery', 'Ready for Delivery'),
    ('out_for_delivery', 'Out for Delivery'),
    ('delivered', 'delivered'),
    ('cancel_requested', 'Cancel Requested'),
    ('canceled', 'canceled'),
    ('return_requested', 'Return Requested'),
    ('returned', 'Returned'),
]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='product_listing_order_items')
    quantity = models.PositiveIntegerField(help_text="Number of units ordered for this product") 

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='order_placed')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit at time of purchase")  # Price of 1 Item 

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price for this product line (quantity × unit_price)")
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

        ## Offer 
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total discount from all offers")
    

    shipped_date = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    cancel_requested = models.BooleanField(default=False)
    cancel_reason = models.TextField(null=True, blank=True)
    cancel_approved = models.BooleanField(default=False)


    return_requested = models.BooleanField(default=False)
    return_reason = models.TextField(null=True, blank=True)
    return_approved = models.BooleanField(default=False)


    def delete(self, *args, **kwargs):
        # Custom logic before deletion
        product_listing = self.product_listing
        product_listing.stock += self.quantity
        product_listing.save()
        print(f"OrderItem for {self.quantity} units of {product_listing} deleted, stock restored")
        
        # Call the parent class's delete method
        super().delete(*args, **kwargs)
        # Update order totals after deletion
        self.order.update_totals()
    

    def save(self, *args, **kwargs):
        # Calculate offer discount if an offer is applied
        self.discount_amount = 0
        self.price = self.product_listing.price
        if not self.pk:
            self.subtotal = (self.quantity * self.price)

            if self.offer and self.offer.is_active and timezone.now() <= self.offer.valid_until:
                if self.offer.offer_type == 'buy_x_get_y':
                    eligible_sets = self.quantity // self.offer.buy_quantity
                    free_items = eligible_sets * self.offer.get_quantity
                    if self.offer.get_discount_percent > 0:
                        self.discount_amount = (self.offer.get_discount_percent / 100) * (self.price * free_items)
                elif self.offer.offer_type == 'bundle':
                    # Bundle logic depends on multiple items; skip unless bundle is verified
                    pass
                elif self.offer.offer_type == 'discount':
                    self.discount_amount = (self.offer.get_discount_percent / 100) * (self.price * self.quantity)

            # Calculate subtotal (price * quantity - discount)

            # Update product listing stock on creation
            if self.product_listing.stock > 0 and not self.pk:
                product_listing = self.product_listing
                product_listing.stock = product_listing.stock - self.quantity  # Subtract ordered quantity
                product_listing.save()
            
            super().save(*args, **kwargs)


        # Set shipped date if status is shipped
        if self.status == "shipped":
            self.shipped_date = timezone.now()

        super().save(*args, **kwargs)
        self.order.update_totals()



    def __str__(self):
        return f"Order_ID: {self.order.id} {self.product_listing.name} ({self.quantity})"
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'


PACKAGE_STATUS_CHOICES = [
    # ('processing', 'Processing'),
    # ('ready_to_deliver', 'Ready to Deliver'),
    ('ready_for_delivery', 'Ready for Delivery'),
    ('out_for_delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
    # ('canceled', 'Canceled'),
]


class DeliveryPackage(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="packages")
    is_return_package = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PACKAGE_STATUS_CHOICES, default="ready_for_delivery")
    delivery_executive = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='de_packages')
    product_listing_count = models.PositiveIntegerField(default=0, help_text="Number of distinct products in this package")
    total_units = models.PositiveIntegerField(default=0, help_text="Total number of items in this package")
    delivery_out_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)  # ready for delivery date
    updated = models.DateTimeField(auto_now=True)

    _updating = False  # Flag to track recursive saves

    def __str__(self):
        return f"Package #{self.id} for Order #{self.order.id}"
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = generate_tracking_number()

        if self.pk:  # Check if the package already exists (i.e., this is an update)
            previous_package = DeliveryPackage.objects.get(pk=self.pk)
            if previous_package.status != self.status:  # Status has changed
                self.update_order_items_status()

        if self.status == "out_for_delivery":
            self.delivery_out_date = timezone.now()
        elif self.status == "delivered":
            self.delivered_date = timezone.now()

        if not self._updating:  # Prevent infinite loop
            self._updating = True
            super().save(*args, **kwargs)
            self._updating = False
        else:
            super().save(*args, **kwargs)

    def update_order_items_status(self):
        """Update the status of all related OrderItems to match the package status."""
        for package_item in self.package_items.all():
            order_item = package_item.order_item
            order_item.status = self.status
            order_item.save()

    def update_package_metrics(self):
        """Update counts based on package items."""
        self.product_listing_count = self.package_items.count()
        self.total_units = self.package_items.aggregate(total=models.Sum('quantity'))['total'] or 0
        self.save(update_fields=['product_listing_count', 'total_units'])

    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'
    

class PackageItem(models.Model):
    package = models.ForeignKey(DeliveryPackage, on_delete=models.CASCADE, related_name="package_items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="order_item_package_item")
    quantity = models.PositiveIntegerField(default=0, help_text="Number of units included in this package")

    def save(self, *args, **kwargs):
        self.quantity = self.order_item.quantity
        super().save(*args, **kwargs)

        # Batch update metrics for multiple items instead of triggering multiple saves
        self.package.update_package_metrics()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.package.update_package_metrics()


    # def clean(self):
    #     if self.quantity > self.order_item.quantity:
    #         raise ValidationError("Package quantity cannot exceed the order item quantity.")

    def __str__(self):
        return f"{self.order_item.product_listing.name} ({self.quantity}) in Package #{self.package.id}"
    

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'