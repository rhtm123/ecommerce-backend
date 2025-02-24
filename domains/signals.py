from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import AllowedDomain

from .utils import update_allowed_domains_cache

@receiver(post_save, sender=AllowedDomain)
def send_order_notification(sender, instance, created, **kwargs):
    update_allowed_domains_cache()
