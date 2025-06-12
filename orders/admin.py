from django.contrib import admin

# Register your models here.

from .models import Order, OrderItem, DeliveryPackage, PackageItem


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order","status","cancel_requested","cancel_approved","return_requested", "return_approved")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    # readonly_fields = ['quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline,]
    list_display = ("id","order_number" ,"user__first_name", "total_amount", "product_listing_count", "payment_status")
    list_filter = ("user",)
    search_fields = ("order_number",)
    readonly_fields = ("order_number", "product_listing_count","total_units")



class PackageItemInline(admin.TabularInline):
    model = PackageItem 
    readonly_fields = ['quantity']

@admin.register(DeliveryPackage)
class DeliveryPackageAdmin(admin.ModelAdmin):
    inlines = [PackageItemInline,]
    search_fields = ("tracking_number",)
    list_display = ("id", "tracking_number", "status", "delivery_out_date", "delivered_date")
    readonly_fields = ("tracking_number", "delivery_out_date", "delivered_date", "product_listing_count","total_units")
