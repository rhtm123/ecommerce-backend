
from django.db import models

class TaxCategory(models.Model):
    name = models.CharField(max_length=50)  # "Standard GST", "Luxury Goods GST"
    details = models.TextField(blank=True, null=True) 
    
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Central GST %
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # State GST %
    igst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Integrated GST %


    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-id']  # Default ordering by 'id'

    def save(self, *args, **kwargs):
        """ Automatically set IGST as CGST + SGST before saving """
        self.igst_rate = self.cgst_rate + self.sgst_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (CGST: {self.cgst_rate}%, SGST: {self.sgst_rate}%)"
    
    
