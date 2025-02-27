from django.contrib import admin

# Register your models here.

from .models import EStore, DeliveryPin

# admin.site.register(EStore)


class DeliveryPinInline(admin.TabularInline):
    model = DeliveryPin
    extra = 1

@admin.register(EStore)
class ProductListingAdmin(admin.ModelAdmin):
    inlines = [DeliveryPinInline,]
    # list_filter = ("estore", 'pin_code')
    list_display = ("name", 'website')

@admin.register(DeliveryPin)
class DeliveryPinAdmin(admin.ModelAdmin):
    list_filter = ("estore", 'pin_code')
    list_display = ("estore", 'pin_code', "city", "state")


