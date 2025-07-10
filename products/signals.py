
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductListing, Product
from django.core.cache import cache

@receiver(post_save, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    try:
        pattern = f"*:/api/product/products/{instance.id}*"
        # print(pattern);
        for key in cache.client.get_client().scan_iter(pattern):
            print("Deleted", key);
            cache.client.get_client().delete(key)

    except Exception as e:
        print(f"Error clearing product cache: {e}")
        print("Non-Redis cache backend detected, clearing all cache.")
        cache.clear()

    # clear product listing cache
    if instance.product_listings.exists():  
        try:
            pattern = f"*:/api/product/product-listings/?product_id={instance.id}*"
            # print(pattern);
            for key in cache.client.get_client().scan_iter(pattern):
                print("Deleted", key);
                cache.client.get_client().delete(key)
        except Exception as e:
            print(f"Error clearing cache: {e}")
            print("Non-Redis cache backend detected, clearing all cache.")
            cache.clear()



@receiver(post_save, sender=ProductListing)
def clear_product_listing_cache(sender, instance, **kwargs):
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