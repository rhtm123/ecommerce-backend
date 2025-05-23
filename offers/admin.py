from django.contrib import admin
from .models import Coupon, Offer, ProductOffer, UserCouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'discount_type',
        'discount_value',
        'coupon_type',
        'is_active',
        'valid_from',
        'valid_until',
        'used_count'
    ]
    list_filter = [
        'is_active',
        'discount_type',
        'coupon_type'
    ]
    search_fields = ['code', 'description']
    readonly_fields = ['used_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value', 'coupon_type')
        }),
        ('Cart Settings', {
            'fields': ('min_cart_value', 'max_discount_amount'),
            'classes': ('collapse',)
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'per_user_limit', 'used_count'),
            'classes': ('collapse',)
        })
    )

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'offer_type',
        'offer_scope',
        'is_active',
        'valid_from',
        'valid_until'
    ]
    list_filter = [
        'is_active',
        'offer_type',
        'offer_scope'
    ]
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Offer Configuration', {
            'fields': ('offer_type', 'offer_scope','get_discount_percent')
        }),
        ('Cart-wide Settings', {
            'fields': ('min_cart_value', 'max_discount_amount'),
            'classes': ('collapse',),
            'description': 'Settings for cart-wide offers'
        }),
        ('Buy X Get Y Settings', {
            'fields': ('buy_quantity', 'get_quantity'),
            'classes': ('collapse',),
            'description': 'Settings for Buy X Get Y type offers'
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        })
    )

class ProductOfferInline(admin.TabularInline):
    model = ProductOffer
    extra = 1
    fields = ['product', 'is_primary', 'bundle_quantity', 'bundle_discount_percent']

    def get_queryset(self, request):
        # Optimize query by selecting related product
        return super().get_queryset(request).select_related('product')

@admin.register(ProductOffer)
class ProductOfferAdmin(admin.ModelAdmin):
    list_display = [
        'offer',
        'product',
        'is_primary',
        'bundle_quantity',
        'bundle_discount_percent'
    ]
    list_filter = ['is_primary', 'offer']
    search_fields = [
        'offer__name',
        'product__name'
    ]
    autocomplete_fields = ['product', 'offer']

# @admin.register(UserCouponUsage)
# class UserCouponUsageAdmin(admin.ModelAdmin):
#     list_display = [
#         'user',
#         'coupon',
#         'used_count',
#         'last_used'
#     ]
#     list_filter = ['coupon']
#     search_fields = [
#         'user__email',
#         'coupon__code'
#     ]
#     readonly_fields = ['last_used']
#     autocomplete_fields = ['user', 'coupon']

#     def has_add_permission(self, request):
#         # Prevent manual creation as these should be created automatically
#         return False