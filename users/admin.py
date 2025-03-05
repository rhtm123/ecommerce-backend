from django.contrib import admin

# Register your models here.
from .models import User, Entity, ShippingAddress, MobileVerification

# admin.site.register(User)

admin.site.register(Entity)

admin.site.register(ShippingAddress)

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
    list_display = ("username", "mobile",)
