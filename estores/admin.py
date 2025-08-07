from django.contrib import admin

# Register your models here.

from .models import EStore, DeliveryPin, ShipCredential, EmailCredential, WhatsAppCredential

# admin.site.register(EStore)

@admin.register(ShipCredential)
class EStoreShipCredentialAdmin(admin.ModelAdmin):
    list_display = ["estore", "is_active", "name", "email", "created", "updated"]


@admin.register(EmailCredential)
class EStoreEmailCredentialAdmin(admin.ModelAdmin): 
    list_display = ["estore", "is_active", "email", "created", "updated"]
    list_filter = ("estore", "is_active")

@admin.register(WhatsAppCredential)
class EStoreWhatsAppCredentialAdmin(admin.ModelAdmin):
    list_display = ["estore", "is_active", "sender_name","auth_token" , "sender_number", "created", "updated"]
    list_filter = ("estore", "is_active")

class DeliveryPinInline(admin.TabularInline):
    model = DeliveryPin
    extra = 1

@admin.register(EStore)
class ProductListingAdmin(admin.ModelAdmin):
    inlines = [DeliveryPinInline,]
    # list_filter = ("estore", 'pin_code')
    list_display = ("name", "id", 'website')

@admin.register(DeliveryPin)
class DeliveryPinAdmin(admin.ModelAdmin):
    list_filter = ("estore", 'pin_code', "city", "state", "cod_available")
    list_display = ("estore", 'pin_code', "city", "state")


