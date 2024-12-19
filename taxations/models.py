
from django.db import models

class TaxCategory(models.Model):
    name = models.CharField(max_length=50)  # e.g., GST 18%
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # 18.00%

    def __str__(self):
        return f"{self.name} ({self.rate}%)"
    