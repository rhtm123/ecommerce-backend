from django.contrib import admin

# Register your models here.

from .models import APIKey  


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_active', 'created_at')
    search_fields = ('name', 'key')
    list_filter = ('is_active', 'created_at')

