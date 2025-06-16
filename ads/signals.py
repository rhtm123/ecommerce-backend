# ads/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Advertisement
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Advertisement)
def clear_ads_cache(sender, **kwargs):

    try:
        client = cache.client.get_client()
        # Adjust pattern based on your cache key structure
        pattern = f"*:/api/ads/advertisements*"

        for key in client.scan_iter(pattern):
            print(f"Deleting cache key: {key}")
            client.delete(key)
    except AttributeError:
        # Fallback for non-Redis backends
        print("Cache client does not support scan_iter, clearing all cache")
        cache.clear()
