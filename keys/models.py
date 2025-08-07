from django.db import models
import secrets

from estores.models import EStore

from encrypted_fields.fields import  EncryptedCharField


# Create your models here.
# models.py
class APIKey(models.Model):
    estore = models.ForeignKey(EStore, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=255)
    key = EncryptedCharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(16)
        super().save(*args, **kwargs)

