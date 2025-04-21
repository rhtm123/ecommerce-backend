from django.contrib import admin
from .models import Coupon, Offer, ProductOffer, UserCouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'coupon_type', 'is_active', 'valid_from', 'valid_until', 'used_count')
    list_filter = ('discount_type', 'coupon_type', 'is_active')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count',)
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'discount_type', 'discount_value', 'coupon_type')
        }),
        ('Cart Settings', {
            'fields': ('min_cart_value', 'max_discount_amount'),
            'classes': ('collapse',)
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'per_user_limit', 'used_count'),
            'classes': ('collapse',)
        })
    )

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'offer_type', 'is_active', 'valid_from', 'valid_until')
    list_filter = ('offer_type', 'is_active')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'offer_type')
        }),
        ('Buy X Get Y Settings', {
            'fields': ('buy_quantity', 'get_quantity', 'get_discount_percent'),
            'classes': ('collapse',)
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        })
    )

@admin.register(ProductOffer)
class ProductOfferAdmin(admin.ModelAdmin):
    list_display = ('offer', 'product', 'is_primary', 'bundle_quantity', 'bundle_discount_percent')
    list_filter = ('offer', 'is_primary')
    search_fields = ('offer__name', 'product__name')
    autocomplete_fields = ['product']

@admin.register(UserCouponUsage)
class UserCouponUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'used_count', 'last_used')
    list_filter = ('coupon',)
    search_fields = ('user__email', 'coupon__code')
    readonly_fields = ('last_used',)