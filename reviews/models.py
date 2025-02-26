from django.db import models

# Create your models here.


from django.db import models

from products.models import ProductListing

from users.models import User
from orders.models import OrderItem


class Review(models.Model):
    product_listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name="product_listing_reviews")
    order_item = models.OneToOneField(OrderItem, on_delete=models.SET_NULL, null=True, blank=True,related_name="order_item_reviews")
    approved = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True , blank=True, related_name="user_reviews")
    rating = models.PositiveSmallIntegerField()  # 1 to 5 scale
    title = models.CharField(max_length=255, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    def __str__(self):
        return  self.title if self.title else "-"
    
    def update_product_listing_reviews(self):
        """Updates the review count and rating in ProductListing"""
        product = self.product_listing
        reviews = product.product_listing_reviews.filter()
        product.review_count = reviews.count()
        product.rating = round(reviews.aggregate(avg_rating=models.Avg("rating"))["avg_rating"] or 0, 1)
        product.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_product_listing_reviews()

    def delete(self, *args, **kwargs):
        """Ensure updates are made when a review is deleted."""
        super().delete(*args, **kwargs)
        self.update_product_listing_reviews()
    
    
