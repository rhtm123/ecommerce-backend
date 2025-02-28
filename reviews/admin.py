from django.contrib import admin

# Register your models here.

from .models import Review

# admin.site.register(Review)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "approved",)