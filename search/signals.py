from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from products.models import ProductListing

# @receiver(post_save, sender=ProductListing)
# def update_document(sender, instance, **kwargs):
#     ProductListingDocument().update(instance)

# @receiver(post_delete, sender=ProductListing)
# def delete_document(sender, instance, **kwargs):
#     ProductListingDocument().delete(instance)
