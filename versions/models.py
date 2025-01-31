from django.db import models

# Create your models here.
from django.template.defaultfilters import slugify


class Version(models.Model):
    name = models.CharField(max_length=24)
    detail = models.TextField()

    is_published = models.BooleanField(default=False)
 
    slug = models.SlugField(max_length=255, null=True, blank=True)
    release_date = models.DateField()
    ## tracking
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now= True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Version, self).save(*args, **kwargs)
