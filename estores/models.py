from django.db import models

# Create your models here.


from cloudinary.models import CloudinaryField

from encrypted_fields.fields import  EncryptedCharField


# from imagekit.models import ProcessedImageField
# from imagekit.processors import ResizeToFill
# from imagekit.models import ImageSpecField

from locations.models import Address

class EStore(models.Model):
    name = models.CharField(max_length=255,)
    website = models.URLField(blank=True, null=True)

    icon = CloudinaryField(
        "icon_image",     
        folder="kb/store/",
        transformation={"width": 240, "height": 240, "crop": "fill"},
        blank=True,
        null=True       
    )
    logo = CloudinaryField(
        "logo_image",
        folder="kb/store/",
        transformation={"crop": "fill"},
        blank=True,
        null=True,
    )

    favicon = CloudinaryField(
        "favicon",
        folder="kb/store/",
        transformation={"width": 32, "height": 32, "crop": "fill"},
        blank=True,
        null=True
    )

    mobile = models.CharField(
        max_length=15,
        help_text="Mobile number for the store",
        null=True,
        blank=True
    )

    social_accounts = models.JSONField(
        default=dict, 
        help_text="Social media accounts in JSON format. Example: {'facebook': 'https://facebook.com/store', 'instagram': 'https://instagram.com/store'}",
        null=True,
        blank=True
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Description of the store"
    )

    tagline = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Tagline for the store"
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

class WebPage(models.Model):
    estore = models.ForeignKey(EStore, null=True, blank=True, on_delete=models.SET_NULL, related_name="estore_static_pages")
    name = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)

    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.estore.name}"
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

class WhatsAppCredential(models.Model):
    estore = models.ForeignKey(EStore, null=True, blank=True, on_delete=models.SET_NULL, related_name="estore_whatsapp_credentials")

    is_active = models.BooleanField(
        default=True,
        help_text="Is this WhatsApp credential active?"
    )

    sender_name = models.CharField(max_length=100, help_text="Name of the sender")
    sender_number = models.CharField(max_length=15)


    templates = models.JSONField(
        default=dict, 
        help_text="Templates for WhatsApp messages in JSON format. Example: {'key': 'template_name', ...}",
        null=True,
        blank=True
    )

    auth_id = models.CharField(
        max_length=100,
    )
    auth_token = EncryptedCharField(
        max_length=255,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender_number} - {self.estore.name}"
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

class ShipCredential(models.Model):
    estore = models.ForeignKey(EStore, null=True, blank=True, on_delete=models.SET_NULL, related_name="estore_shiprocket_credentials")
    is_active = models.BooleanField(
        default=True,
        help_text="Is this credential active?"
    )
    name = models.CharField(
        max_length=100,         
        help_text="Name of the service example - ShipRocket, Delhivery, etc."
    )
    email = models.EmailField(
        max_length=255,         
        help_text="Email associated with account"
    )
    password = EncryptedCharField(
        max_length=255,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.estore.name}"
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

class EmailCredential(models.Model):
    estore = models.ForeignKey(EStore, null=True, blank=True, on_delete=models.SET_NULL, related_name="estore_email_send_credentials")
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this email send credential active?"
    )

    host = models.CharField(
        max_length=255, 
        help_text="SMTP host for sending emails"
    )

    email = models.EmailField(
        max_length=255,
        help_text="Email address used for sending emails"
    )
    password = EncryptedCharField(
        max_length=255,
        help_text="Password for the email account"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.estore.name}"
    
    class Meta:
        ordering = ['-id']  # Default ordering by 'id'
