# Create your models here.

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# from imagekit.models import ProcessedImageField
# from imagekit.processors import ResizeToFill
# from imagekit.models import ImageSpecField

from location.models import Address


class User(AbstractUser):
    mobile = models.CharField(max_length=15, null=True, blank=True)
    alternate_mobile = models.CharField(max_length=15, null=True, blank=True)

    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='buyer',
        help_text="available choices -> buyer, seller"                
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



class Entity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Foreign key to the User model
    name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    entity_type = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,blank=True, null=True)

    is_default = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)