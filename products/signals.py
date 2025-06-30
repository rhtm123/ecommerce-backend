
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductListing
from django.core.cache import cache




@receiver(post_save, sender=ProductListing)
def clear_order_cache(sender, instance, **kwargs):
    try:
        pattern = f"*:/api/product/product-listings/slug/{instance.slug}*"
        # print(pattern);
        for key in cache.client.get_client().scan_iter(pattern):
            print("Deleted", key);
            cache.client.get_client().delete(key)
    except Exception as e:
        print(f"Error clearing order cache: {e}")
        print("Non-Redis cache backend detected, clearing all cache.")
        cache.clear()