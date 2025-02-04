from django.db import models

# Create your models here.


from django.db import models

from products.models import ProductListing

from users.models import User
from orders.models import OrderItem


class Review(models.Model):
    product_listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name="listing_reviews")
    order_item = models.OneToOneField(OrderItem, on_delete=models.SET_NULL, null=True, blank=True,related_name="order_item_reviews")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True , blank=True, related_name="user_reviews")
    rating = models.PositiveSmallIntegerField()  # 1 to 5 scale
    title = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.title if self.title else "-"
