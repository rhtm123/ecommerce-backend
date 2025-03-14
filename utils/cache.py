from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse

def cache_response(timeout=60*15, cache_key_func=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            key = cache_key_func(request, *args, **kwargs) if cache_key_func else f"cache:{request.path}"
            cached = cache.get(key)
            if cached is not None:
                return JsonResponse(cached)
            response = view_func(request, *args, **kwargs)
            if isinstance(response, dict):  # Ensure response is cacheable
                cache.set(key, response, timeout=timeout)
                return JsonResponse(response)
            return response
        return wrapped_view
    return decorator