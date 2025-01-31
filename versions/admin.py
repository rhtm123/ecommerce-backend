from django.contrib import admin

# Register your models here.

from .models import Version

from django_summernote.admin import SummernoteModelAdmin

class VersionAdmin(SummernoteModelAdmin):
    summernote_fields = ('detail',)
    list_display = ('name', "is_published" ,"release_date",)
    list_filter = ('is_published',)


admin.site.register(Version, VersionAdmin)