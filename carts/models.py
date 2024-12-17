from django.db import models

from users.models import User
from products.models import ProductListing
# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL , related_name="user_carts", null=True, blank=True)
    purchased = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, related_name="cart_items", null=True, blank=True)
    product_listing = models.ForeignKey(ProductListing, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL , related_name="user_wishlists", null=True, blank=True)
    name = models.CharField(max_length=255, default="My Wishlist")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.SET_NULL, related_name="wishlist_items", null=True, blank=True)
    product_listing = models.ForeignKey(ProductListing, on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)