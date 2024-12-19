from django.contrib import admin

# Register your models here.
from .models import TaxCategory

admin.site.register(TaxCategory)