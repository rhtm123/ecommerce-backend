from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Category

from django.contrib import admin
from .models import Category
from django.utils.safestring import mark_safe


class MyAdmin(TreeAdmin):
    form = movenodeform_factory(Category)

admin.site.register(Category, MyAdmin)


from django.contrib import admin
from .models import Product, ProductListing, ProductListingImage, Variant


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1


class ProductListingImageInline(admin.TabularInline):
    model = ProductListingImage
    extra = 1
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height: 75px;" />')
        return "No Image"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [VariantInline,]

@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    inlines = [ProductListingImageInline]

