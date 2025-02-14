from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from utils.send_whatsapp import send_wa_msg
from utils.constants import wa_content_templates
from .models import Order, DeliveryPackage
from utils.send_email import send_mail_thread

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    print("Sending order notification")
    if created:  # The instance is new (not yet saved)
        mobile = instance.user.mobile
        receiver_email = instance.user.email
        name = f"{instance.user.first_name} {instance.user.last_name}"
        order_id = str(instance.id)
        total_items = str(instance.product_listing_count)
        # print(name, order_id, total_items)

        try:
            with open("./utils/htmlemails/html_order.html", "r", encoding="utf-8") as file:
                email_content = file.read()
                formatted_email = email_content.replace("{name}", name).replace("{order_id}", order_id).replace("{total_items}", total_items)
                subject = f"Naigaon Market notification: #Order{order_id} placed successfully"
                text_content = subject

                print("Email sent successfully")
                
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
            content_template_sid = wa_content_templates["order_sid"]
            variables = {
                '1': name,
                '2': order_id,
                '3': total_items,
            }
            # Uncomment to send WhatsApp message
            print("WA message sent!!")
            # send_wa_msg(content_template_sid, variables, mobile)
        except Exception as e:
            print(f"WhatsApp message send failed: {e}")



@receiver(post_save, sender=DeliveryPackage)
def send_order_notification(sender, instance, created, **kwargs):
    # print("Sending Package notification")
    mobile = instance.order.user.mobile
    receiver_email = instance.order.user.email
    name = f"{instance.order.user.first_name} {instance.order.user.last_name}"
    tracking_number = str(instance.tracking_number)
    total_items = str(instance.product_listing_count)
    status = str(instance.status)

    if instance.delivery_executive:
        de_name = f"{instance.delivery_executive.first_name} {instance.delivery_executive.last_name}"
        de_mobile = instance.delivery_executive.mobile
    else:
        de_name = "Naigaon Market"
        de_mobile = "9518901902"
    # print(name, order_id, total_items)

    if status=="out_for_delivery":
        print ("Out for Delivery Notification")

        try:
            with open("./utils/htmlemails/html_order.html", "r", encoding="utf-8") as file:
                email_content = file.read()
                formatted_email = email_content.replace("{name}", name).replace("{tracking_number}", tracking_number).replace("{total_items}", total_items)
                subject = f"Naigaon Market notification: #Order{tracking_number} placed successfully"
                text_content = subject

                print("Email sent successfully")
                
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

            content_template_sid = wa_content_templates["delivery_out_sid"]
            variables = {
                'name': name,
                'package_number': tracking_number,
                'no_of_items': total_items,
                'de_name': de_name,
                'de_mobile': de_mobile
            }
            # Uncomment to send WhatsApp message
            print("WA message sent!!")
            send_wa_msg(content_template_sid, variables, mobile)
        except Exception as e:
            print(f"WhatsApp message send failed: {e}")

    if status== "delivered":
        
        try:
            ## email send 
            pass 
        except:
            pass 
            
        
        try:
            content_template_sid = wa_content_templates["delivered_sid"]
            variables = {
                'customer_name': name,
                'package_number': tracking_number,
                'no_of_items': total_items,
                'feedback_link': "https://naigaonmarket.com",
            }
            # Uncomment to send WhatsApp message
            print("WA message sent!!")
            send_wa_msg(content_template_sid, variables, mobile)
        except Exception as e:
            print(f"WhatsApp message send failed: {e}")