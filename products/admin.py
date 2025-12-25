from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from .models import Category

from django.contrib import admin
from .models import Category
from django import forms


from django.db import models
from django_json_widget.widgets import JSONEditorWidget




# from django.utils.safestring import mark_safe





from django.contrib import admin
from .models import ReturnExchangePolicy, Product, ProductListing, ProductListingImage, Variant

from .models import FeatureGroup, FeatureTemplate, Feature

from django_summernote.admin import SummernoteModelAdmin


class MyAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    list_display = ["name","id" ,"level" ,"estore","approved"]
    list_filter = ['level', "estore", "approved"]
    search_fields = ("name",)


admin.site.register(Category, MyAdmin)

admin.site.register(ReturnExchangePolicy)
admin.site.register(FeatureGroup)
admin.site.register(FeatureTemplate)
admin.site.register(Feature)

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


class VariantInline(admin.TabularInline):
    model = Variant
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
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


class ProductListingForm(forms.ModelForm):
    class Meta:
        model = ProductListing
        fields = '__all__'

    class Media:
        js = ('admin/js/jquery.init.js', 'admin/js/product_variant_filter.js',)



@admin.register(ProductListing)
class ProductListingAdmin(admin.ModelAdmin):
    form = ProductListingForm
    inlines = [ProductListingImageInline]
    readonly_fields = ("name", "tax_category", "brand", "slug", "category", )
    list_display = ("name", "make_id", "id", "variant", "approved", "brand", "seller", "category", "price", "mrp", "stock" )
    search_fields = ("name",)
    list_filter = ("category", 'brand', 'seller', 'approved')
    actions = ['approve_product_listings', "unapprove_product_listings", "make_out_of_stock"]

    def approve_product_listings(self, request, queryset):
        queryset.update(approved=True)

    def unapprove_product_listings(self, request, queryset):
        queryset.update(approved=False)
    
    def make_out_of_stock(self, request, queryset):
        queryset.update(stock=0)