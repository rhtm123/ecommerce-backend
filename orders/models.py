from django.db import models
from users.models import ShippingAddress
from products.models import ProductListing

from django.conf import settings
from users.models import Entity

from estores.models import EStore





class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    tracking_number = models.CharField(max_length=255, blank=True, null=True)

    total_items = models.PositiveIntegerField(default=1, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    # discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    

    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of 1 Item 
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_listing.name} ({self.quantity})"

