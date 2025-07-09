from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from pydantic import BaseModel
from ninja import Schema, ModelSchema  # ✅ Import these

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

            # Support caching for Pydantic models, dicts, lists
            if isinstance(response, (BaseModel, Schema, ModelSchema)):
                data = response.model_dump()
            elif isinstance(response, (dict, list)):
                data = response
            else:
                # Do not cache non-serializable or HttpResponse types
                return response

            print("Storing to cache")
            cache.set(key, json.dumps(data, default=str), timeout=timeout)
            return JsonResponse(data, safe=False)
        

        return wrapped_view

    return decorator
