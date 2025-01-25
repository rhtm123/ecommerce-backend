from django.core.cache import cache
from .models import AllowedDomain

def update_allowed_domains_cache():
    allowed_domains = list(
        AllowedDomain.objects.filter(is_active=True).values_list('domain', flat=True)
    )
    cache.set('allowed_domains', allowed_domains, timeout=3600)  # Cache for 1 hour

def get_allowed_domains():
    allowed_domains = cache.get('allowed_domains')
    if not allowed_domains:  # If cache is empty, load from DB and update cache
        allowed_domains = list(
            AllowedDomain.objects.filter(is_active=True).values_list('domain', flat=True)
        )
        cache.set('allowed_domains', allowed_domains, timeout=3600)
    return allowed_domains