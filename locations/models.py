# Create your models here.
from django.db import models


class Address(models.Model):
    line1 = models.CharField(max_length=255)  # Flat/Apartment/Building
    line2 = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True, default="India")
    pin = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True,)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    google_map_url = models.URLField(max_length=500, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.line1}"