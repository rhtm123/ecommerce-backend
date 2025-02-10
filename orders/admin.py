from django.contrib import admin

# Register your models here.

from .models import Order, OrderItem, DeliveryPackage, PackageItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline,]


class PackageItemInline(admin.TabularInline):
    model = PackageItem 

@admin.register(DeliveryPackage)
class DeliveryPackageAdmin(admin.ModelAdmin):
    inlines = [PackageItemInline,]