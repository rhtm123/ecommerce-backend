from django.db import models

# Create your models here.
from django.db import models

class AllowedDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)  # Unique constraint for faster lookups
    is_active = models.BooleanField(default=True)  # Allow enabling/disabling domains dynamically

    emails = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain