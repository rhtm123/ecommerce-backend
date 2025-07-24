from django.contrib import admin

# Register your models here.
from .models import User, Entity, ShippingAddress, MobileVerification

# admin.site.register(User)

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name","id","entity_type","user", "website", "featured")
    search_fields = ("name",)
    list_filter = ("entity_type",)
     

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("user","name","address", "mobile","type", "is_default")



admin.site.register(MobileVerification)


class EntityInline(admin.TabularInline):
    model = Entity
    extra = 1

 
class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [EntityInline, ShippingAddressInline] 
    list_display = ("username", "mobile","mobile_verified")
