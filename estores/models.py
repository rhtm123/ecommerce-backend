from django.db import models

# Create your models here.


from cloudinary.models import CloudinaryField


# from imagekit.models import ProcessedImageField
# from imagekit.processors import ResizeToFill
# from imagekit.models import ImageSpecField

from locations.models import Address

class EStore(models.Model):
    name = models.CharField(max_length=255,)
    website = models.URLField(blank=True, null=True)
    logo = CloudinaryField(
        "image",
        folder="kb/store/",
        transformation={"width": 600, "height": 600, "crop": "fill"},
        blank=True,
        null=True,
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE,blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'
