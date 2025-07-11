# auth.py
from ninja.security import APIKeyHeader

from django.core.cache import cache
from .models import APIKey

CACHE_KEY = "valid_api_keys"
TTL = 60 * 5  # 5 minutes

def load_api_keys():
    """Load keys from DB to cache."""
    keys = APIKey.objects.filter(is_active=True).values_list("key", "name")
    key_map = {k: v for k, v in keys}
    cache.set(CACHE_KEY, key_map, timeout=TTL)
    return key_map

def get_cached_api_keys():
    """Get from cache or reload if missing."""
    keys = cache.get(CACHE_KEY)
    # print(keys)
    if keys is None:
        keys = load_api_keys()
    return keys



class APIKeyAuth(APIKeyHeader):
    param_name = "X-API-KEY"

    def authenticate(self, request, key):
        key_map = get_cached_api_keys()
        if key in key_map:
            request.api_key_name = key_map[key]
            return key
        return None


# from ninja import NinjaAPI
# from .auth import APIKeyAuth

# api_key_auth = APIKeyAuth()
# api = NinjaAPI()

# @api.get("/dashboard", auth=api_key_auth)
# def dashboard(request):
#     return {"message": f"Hello {request.api_key_name}"}