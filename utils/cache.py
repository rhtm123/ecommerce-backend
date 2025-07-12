import json
from functools import wraps
from django.http import JsonResponse
from pydantic import BaseModel
from ninja.schema import Schema
from ninja.orm import ModelSchema
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.db.models import Model
from django.forms.models import model_to_dict


def convert_pydantic(obj):
    """Recursively convert Pydantic models to dicts"""
    if isinstance(obj, QuerySet):
        obj = list(obj)
    if isinstance(obj, (BaseModel, Schema, ModelSchema)):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: convert_pydantic(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_pydantic(v) for v in obj]
    elif isinstance(obj, Model):
        return model_to_dict(obj)
    return obj

def cache_response(timeout=60 * 15, cache_key_func=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            print("Cache function called")

            query_params = request.GET.urlencode()
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

            # Convert nested Pydantic objects to dict
            data = convert_pydantic(response)

            print("Storing to cache")
            cache.set(key, json.dumps(data, default=str), timeout=timeout)
            return JsonResponse(data, safe=False)

        return wrapped_view
    return decorator
