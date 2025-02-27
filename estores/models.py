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




class DeliveryPin(models.Model):
    estore = models.ForeignKey(EStore, null=True, blank=True, on_delete=models.SET_NULL, related_name="estore_delivery_pins")
    pin_code = models.CharField(max_length=10)

    city = models.CharField(
        max_length=100,
        null=True,  # Optional if you add it
        blank=True,
        help_text="City associated with the PIN code"
    )
    state = models.CharField(
        max_length=100,
        null=True,  # Optional if you add it
        blank=True,
        help_text="State associated with the PIN code"
    )

    cod_available = models.BooleanField(
        default=True,
        help_text="Is cash on delivery available for this PIN?"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pin_code} {self.estore.name}"
    

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'
        unique_together = ('estore', 'pin_code')  # Ensure no duplicate store-PIN combinations
