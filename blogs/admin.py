from django.contrib import admin

# Register your models here.

from .models import Blog, Tag 
from django_summernote.admin import SummernoteModelAdmin



# admin.site.register(Blog)

class BlogModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
    summernote_fields = ['content']

admin.site.register(Blog, BlogModelAdmin)


admin.site.register(Tag)