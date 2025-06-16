from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ShippingAddress
from django.core.cache import cache


@receiver([post_save, post_delete], sender=ShippingAddress)
def clear_cache(sender, instance, **kwargs):
    print("Clearing shipping address cache...")

    print(instance.user.id);

    try:
        client = cache.client.get_client()
        
        # Print all keys for debugging
        for key in client.scan_iter("*"):
            print(f"Cache key: {key.decode() if isinstance(key, bytes) else key}")

        pattern = f"*cache:/api/user/shipping-addresses*user_id={instance.user.id}*"

        for key in client.scan_iter(pattern):
            decoded_key = key.decode() if isinstance(key, bytes) else key
            print(f"Deleting cache key: {decoded_key}")
            client.delete(key)

    except AttributeError:
        print("Non-Redis cache backend detected, clearing all cache.")
        cache.clear()
