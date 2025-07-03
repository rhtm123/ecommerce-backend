from django.contrib import admin

# Register your models here.
from .models import TaxCategory


@admin.register(TaxCategory)
class TaxCategoryAdmin(admin.ModelAdmin):
    list_display = ("name","id","cgst_rate","sgst_rate","igst_rate")
    search_fields = ("name",)
