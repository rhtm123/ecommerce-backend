from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Category

from django.contrib import admin
from .models import Category
# from django.utils.safestring import mark_safe


class MyAdmin(TreeAdmin):
    form = movenodeform_factory(Category)

admin.site.register(Category, MyAdmin)


from django.contrib import admin
from .models import ReturnExchangePolicy, Product, ProductListing, ProductListingImage, Variant

from .models import FeatureGroup, FeatureTemplate, Feature

from django_summernote.admin import SummernoteModelAdmin



admin.site.register(ReturnExchangePolicy)
admin.site.register(FeatureGroup)
admin.site.register(FeatureTemplate)
admin.site.register(Feature)

admin.site.register(Variant)


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1


class ProductListingImageInline(admin.TabularInline):
    model = ProductListingImage
    extra = 1
    # readonly_fields = ["image_preview"]

    # def image_preview(self, obj):
    #     if obj.image:
    #         return mark_safe(f'<img src="{obj.image.url}" style="height: 75px;" />')
    #     return "No Image"

@admin.register(Product)
class ProductAdmin(SummernoteModelAdmin):
    summernote_fields = ['description',]
    inlines = [VariantInline,]
    # raw_id_fields = ("brand",)
    list_display = ("name", "is_service", "tax_category")
    search_fields = ("name",)
    list_filter = ("category",)

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    inlines = [ProductListingImageInline]
    readonly_fields = ("name", "tax_category", "brand", "slug", "category", )
    list_display = ("name", "variant", "brand", "seller", "category", "price", "mrp", "is_service")
    search_fields = ("name",)
    list_filter = ("category", 'brand', 'seller', 'approved')

