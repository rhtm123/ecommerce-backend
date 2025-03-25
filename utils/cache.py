from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from pydantic import BaseModel
import json


def cache_response(timeout=60 * 15, cache_key_func=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            print("Cache function called")

            # Generate cache key with query parameters
            query_params = request.GET.urlencode()  # Convert query parameters to a string
            key = (
                cache_key_func(request, *args, **kwargs)
                if cache_key_func
                else f"cache:{request.path}?{query_params}"
            )

            cached = cache.get(key)
            if cached is not None:
                print("Returning from cache")
                return JsonResponse(json.loads(cached), safe=False)

            response = view_func(request, *args, **kwargs)

            # Ensure response is cacheable (if it's a Pydantic model)
            if isinstance(response, BaseModel):
                print("Storing to cache")
                cache.set(key, response.model_dump_json(), timeout=timeout)
                return JsonResponse(json.loads(response.model_dump_json()), safe=False)

            return response

        return wrapped_view

    return decorator
