from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from utils.send_whatsapp import send_wa_msg
from utils.constants import wa_content_templates
from .models import Order
from utils.send_email import send_mail_thread

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    print("Sending order notification")
    if created:  # The instance is new (not yet saved)
        mobile = instance.user.mobile
        receiver_email = instance.user.email
        name = f"{instance.user.first_name} {instance.user.last_name}"
        order_id = str(instance.id)
        total_units = str(instance.product_listing_count)
        # print(name, order_id, total_items)

        try:
            with open("./utils/htmlemails/html_order.html", "r", encoding="utf-8") as file:
                email_content = file.read()
                formatted_email = email_content.replace("{name}", name).replace("{order_id}", order_id).replace("{total_items}", total_items)
                subject = f"Naigaon Market notification: #Order{order_id} placed successfully"
                text_content = subject
                
                # Uncomment to send email
                # send_mail_thread(
                #     subject=subject,
                #     body=text_content,
                #     from_email=settings.EMAIL_HOST_USER,
                #     recipient_list=[receiver_email],  # Modify as needed
                #     html=formatted_email
                # )
        except Exception as e:
            print(f"Email send failed: {e}")

        try:
            content_template_sid = wa_content_templates["content_template_order_sid"]
            variables = {
                '1': name,
                '2': order_id,
                '3': total_items,
            }
            # Uncomment to send WhatsApp message
            # send_wa_msg(content_template_sid, variables, mobile)
        except Exception as e:
            print(f"WhatsApp message send failed: {e}")
