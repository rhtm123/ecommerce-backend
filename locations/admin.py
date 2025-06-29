from django.contrib import admin


from .models import Address 



@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("line1", 'line2', "city", "pin")