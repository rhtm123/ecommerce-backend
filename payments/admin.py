from django.contrib import admin

# Register your models here.

from .models import Payment 

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    search_fields = ("order", "transaction_id",)
    list_filter = ("transaction_id",)
    list_display = ("order", "transaction_id" ,"status", "amount")