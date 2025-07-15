# Create your models here.

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from locations.models import Address
from estores.models import EStore

from cloudinary.models import CloudinaryField



from django.utils.timezone import now
from datetime import timedelta



class MobileVerification(models.Model):
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.created >= now() - timedelta(minutes=10)  # OTP expires in 5 minutes
    


class User(AbstractUser):
    mobile = models.CharField(max_length=15, null=True, blank=True)
    mobile_verified = models.BooleanField(default=False)

    alternate_mobile = models.CharField(max_length=15, null=True, blank=True)

    google_picture = models.URLField(blank=True, null=True)

    GENDER_CHOICES = [
        ("",""),
        ('male', 'male'),
        ('female', 'female'),
        ("other", 'other'),
    ]

    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=True, blank=True);

    is_restricted = models.BooleanField(default=False, help_text="Indicates if the user is restricted from making purchases.")

    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_users")

    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('entity', 'Entity'),
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='buyer',
        help_text="available choices -> buyer, entity"                
    )

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Custom related name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permission_set",  # Custom related name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    def __str__(self):
        return self.username



class Entity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_entities", null=True, blank=True)  # Foreign key to the User model
    name = models.CharField(max_length=255, help_text="Name of the entity")
    gst_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, null=True, blank=True, related_name="estore_entities")

    
    ENTITY_TYPE_CHOICES = [
        ('brand', 'Brand'),
        ('seller', 'Seller'),
        ('manufacturer', 'Manufacturer'),
        ('packager', 'Packager'),
    ]

    featured = models.BooleanField(default=False)
    
    entity_type = models.CharField(
        max_length=255,
        choices=ENTITY_TYPE_CHOICES,
        help_text='Specify the type of entity.'
    )

    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)

    logo = CloudinaryField(
        "image",
        folder="kb/entity/",
        transformation={"width": 600, "height": 600, "crop": "fill"},
        blank=True,
        null=True,
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'


    def __str__(self):
        return self.name


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,blank=True, null=True)
    type = models.CharField(max_length=100, default="home", blank=True, null=True)
    is_default = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    def __str__(self):
        return f'{self.user.email} {self.address.line1}'