from django.shortcuts import render

# Create your views here.


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AllowedDomain

@receiver([post_save, post_delete], sender=AllowedDomain)
def update_cache_on_change(sender, **kwargs):
    from domain.utils import update_allowed_domains_cache
    update_allowed_domains_cache()