from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import AllowedDomain

@admin.register(AllowedDomain)
class AllowedDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'is_active')
    search_fields = ('domain',)
