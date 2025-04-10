from django.db import models
from cloudinary.models import CloudinaryField

from estores.models import EStore


class Advertisement(models.Model):
    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, related_name="estore_ads")
    title = models.CharField(max_length=255)
    image = CloudinaryField(
        "image",
        folder="kb/ads/",
        transformation={"width": 1200, "height": 720, "crop": "fill"},
        blank=True,
        null=True,
    )
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

    created = models.DateTimeField(auto_now_add=True)

    def is_currently_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date

    def __str__(self):
        return self.title
