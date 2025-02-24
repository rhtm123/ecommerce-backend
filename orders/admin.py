from django.contrib import admin

# Register your models here.

from .models import Order, OrderItem, DeliveryPackage, PackageItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline,]
    readonly_fields = ("order_number", "product_listing_count","total_units")


class PackageItemInline(admin.TabularInline):
    model = PackageItem 
    readonly_fields = ['quantity']

@admin.register(DeliveryPackage)
class DeliveryPackageAdmin(admin.ModelAdmin):
    inlines = [PackageItemInline,]
    readonly_fields = ("tracking_number", "delivery_out_date", "delivered_date", "product_listing_count","total_units")
