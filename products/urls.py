from django.urls import path
from .views import get_variants_for_product

urlpatterns = [
    path('admin/get-variants/', get_variants_for_product, name='get_variants_for_product'),
]
