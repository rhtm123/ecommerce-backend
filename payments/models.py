from django.db import models

from orders.models import Order

from utils.payment import create_payment

from estores.models import EStore

from uuid import uuid4


# First, define the PAYMENT_CHOICES if not already defined
PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
)



# Add this new Payment model
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    estore = models.ForeignKey(EStore, on_delete=models.SET_NULL, null=True, blank=True, related_name="estore_payments")
    payment_method = models.CharField(
        max_length=50,
        default="pg"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=PAYMENT_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True) # merchant_order_id
    payment_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # Additional fields you might want
    payment_gateway = models.CharField(max_length=50, blank=True, null=True, default="PhonePe")  # e.g., Stripe, PayPal
    payment_url = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            merchant_order_id = str(uuid4())  # Generate unique order ID
            if self.payment_method=="pg":
                merchant_order_id, standard_pay_response = create_payment(amount=self.amount, estore=self.estore)
                self.payment_url = standard_pay_response.redirect_url;
            self.transaction_id = merchant_order_id
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.amount}"
    