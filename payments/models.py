from django.db import models

from orders.models import Order

from utils.payment import create_payment

from estores.models import EStore

from uuid import uuid4

from django.core.cache import cache



# First, define the PAYMENT_CHOICES if not already defined
PAYMENT_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
)

PLATFORM_CHOICES = (
    ('web', 'Web'),
    ('mobile', 'Mobile'),
    ('api', 'API'),
)


# Add this new Payment model
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    estore = models.ForeignKey(EStore, on_delete=models.SET_NULL, null=True, blank=True, related_name="estore_payments")
    payment_method = models.CharField(
        max_length=50,
        default="pg"
    ) # pg (payment gateway) or cod
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=PAYMENT_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Gateway-specific ID (PhonePe order_id or Cashfree cf_link_id)")
    payment_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # Additional fields you might want
    payment_gateway = models.CharField(max_length=50, blank=True, null=True, default="PhonePe")  # e.g., Stripe, PayPal (keeping for backward compatibility)
    payment_url = models.TextField(blank=True, null=True)
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        default='web'
    )
    device_info = models.JSONField(
        blank=True, 
        null=True,
        help_text="Store device information for mobile payments"
    )
    
    def generate_redirect_url(self, merchant_order_id):
        """
        Generate platform-specific redirect URL
        """
        if self.platform == 'mobile':
            # For mobile apps, use deep link URL
            return f"naigaonmarketapp://payment?transaction_id={merchant_order_id}&order_id={self.order.id}"
        else:
            # For web, use traditional website URL
            base_url = getattr(self.estore, 'website', 'https://kb.thelearningsetu.com') if self.estore else 'https://kb.thelearningsetu.com'
            if base_url[-1] == "/":
                return f"{base_url}checkout/{merchant_order_id}"
            else:
                return f"{base_url}/checkout/{merchant_order_id}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            merchant_order_id = str(uuid4())
            self.transaction_id = merchant_order_id

            if not self.platform:
                self.platform = 'web'
                            
            if self.payment_method == "pg":
                # Default to PhonePe if no gateway specified
                gateway = self.payment_gateway or "PhonePe"
                
                # Generate platform-specific redirect URL
                redirect_url = self.generate_redirect_url(merchant_order_id)
                
                # Get customer details from order if available (for Cashfree)
                customer_details = None
                if self.order and hasattr(self.order, 'user'):
                    user = self.order.user
                    name = user.first_name + " " + user.last_name
                    customer_details = {
                        "customer_name": name,
                        "customer_email": getattr(user, 'email', '[email protected]') or '[email protected]',
                        "customer_phone": getattr(user, 'mobile', '9999999999') or '9999999999'
                    }
                
                # Create payment with selected gateway
                standard_pay_response = create_payment(
                    amount=self.amount,
                    redirect_url=redirect_url,
                    merchant_order_id=merchant_order_id,
                    gateway=gateway,
                    customer_details=customer_details,
                    link_purpose=f"Payment for Order #{self.order.id}"
                )
                
                # Handle payment URL from both gateways
                self.payment_url = (
                    standard_pay_response.get("redirectUrl") or 
                    standard_pay_response.get("link_url") or
                    standard_pay_response.get("redirect_url")
                )
            
        order = self.order
        order.payment_status = self.status  # Update the order status to match the payment status
        order.save()  # Save the updated

        cache_key = f"cache:/api/order/orders/?items_needed=true&user_id={self.order.user.id}&ordering=-id"
        cache.delete(cache_key)
        super().save(*args, **kwargs)


    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        platform_str = f" ({self.platform})" if self.platform != 'web' else ""
        return f"Payment for Order #{self.order.id} - {self.amount}{platform_str}"
    