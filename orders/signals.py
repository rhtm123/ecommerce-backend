import threading
import time
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from utils.send_whatsapp import send_wa_msg, send_wa_msg_plivo
from utils.constants import wa_content_templates, wa_plivo_templates
from .models import Order, DeliveryPackage, OrderItem
from utils.send_email import send_mail_thread
from django.conf import settings
from django.core.cache import cache
from django.db.models import Prefetch

def get_order_items_by_seller(order):
    # Query order items for the given order, prefetching product listing and seller
    order_items = order.order_items.prefetch_related('product_listing__seller').all()
    
    # Group order items by seller
    items_by_seller = {}
    for item in order_items:
        seller = item.product_listing.seller  # Assuming seller is a field in ProductListing
        if seller not in items_by_seller:
            items_by_seller[seller] = []
        items_by_seller[seller].append(item)
    
    return items_by_seller


@receiver(post_save, sender=Order)
def clear_order_cache(sender, instance, **kwargs):
    pattern = f"*:/api/order/orders*user_id={instance.user.id}*"   
    for key in cache.client.get_client().scan_iter(pattern):
        cache.client.get_client().delete(key)

@receiver(post_save, sender=OrderItem)
def clear_order_cache(sender, instance, **kwargs):
    pattern = f"*:/api/order/order-items*order_id={instance.order.id}*" 
    for key in cache.client.get_client().scan_iter(pattern):
        cache.client.get_client().delete(key)

@receiver(post_save, sender=DeliveryPackage)
def clear_delivery_package_cache(sender, instance, **kwargs):
    pattern = f"*:/api/order/delivery-packages*order_id={instance.order.id}*" 
    for key in cache.client.get_client().scan_iter(pattern):
        cache.client.get_client().delete(key)


@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        order_id = instance.id  # Capture only the ID, not the full instance

        def delayed_order_notification():
            time.sleep(5)  # 2-second delay to allow OrderItem updates
            # Fetch the latest Order instance from the database
            order = Order.objects.get(id=order_id)
            mobile = order.user.mobile
            receiver_email = order.user.email
            name = f"{order.user.first_name} {order.user.last_name}"
            order_number = str(order.order_number)
            total_items = str(order.product_listing_count)

            items_by_seller = get_order_items_by_seller(order) 

            for seller, items in items_by_seller.items():
                if seller:
                    seller_name = seller.name
                    # print(f"Seller: {seller.name}")  # Assuming seller has a name field
                    template_name = wa_plivo_templates["seller_notify_sid"]
                    variables = [seller_name, order_number, len(items)]
                    print(template_name)
                    print(variables)
                    print("WA message sent to seller!!")
                    send_wa_msg_plivo(template_name, variables, mobile)

            try:
                with open("./utils/htmlemails/html_order.html", "r", encoding="utf-8") as file:
                    email_content = file.read()
                    formatted_email = email_content.replace("{name}", name).replace("{order_number}", order_number).replace("{total_items}", total_items,).replace("{tracking_url}", f"https://www.naigaonmarket.com/profile/orders/{order_number}").replace('{unsubscribe_url}', f"https://www.naigaonmarket.com/profile/unsubscribe-email?email={receiver_email}")
                    subject = f"Naigaon Market : #Order{order_number} placed successfully"
                    text_content = subject
                    print("Email sent successfully")
                    # Uncomment to send email
                    ## working now !!
                    # send_mail_thread(
                    #     subject=subject,
                    #     body=text_content,
                    #     from_email=settings.EMAIL_HOST_USER,
                    #     recipient_list=[receiver_email],
                    #     html=formatted_email
                    # )
            except Exception as e:
                print(f"Email send failed: {e}")

            try:
                # content_template_sid = wa_content_templates["order_sid"]
                # variables = {'1': name, '2': order_number, '3': total_items}
    
                # send_wa_msg(content_template_sid, variables, mobile)
                
                variables = [name, order_number, total_items]
                template_name = wa_plivo_templates["order_sid"]
                print("WA message sent!!")
                send_wa_msg_plivo(template_name, variables, mobile)
            except Exception as e:
                print(f"WhatsApp message send failed: {e}")

        # Run after the transaction commits
        transaction.on_commit(lambda: threading.Thread(target=delayed_order_notification).start())

@receiver(post_save, sender=DeliveryPackage)
def send_package_notification(sender, instance, created, **kwargs):
    if kwargs.get("update_fields") == {"product_listing_count", "total_units"}:
        return  # Ignore saves triggered by update_package_metrics

    package_id = instance.id  # Capture only the ID, not the full instance

    def delayed_package_notification():
        time.sleep(2)  # 2-second delay to allow updates
        # Fetch the latest DeliveryPackage instance from the database
        package = DeliveryPackage.objects.get(id=package_id)
        mobile = package.order.user.mobile
        receiver_email = package.order.user.email
        name = f"{package.order.user.first_name} {package.order.user.last_name}"
        tracking_number = str(package.tracking_number)
        total_items = str(package.product_listing_count)
        status = str(package.status)
        order_number = package.order.order_number

        if package.delivery_executive:
            de_name = f"{package.delivery_executive.first_name} {package.delivery_executive.last_name}"
            de_mobile = package.delivery_executive.mobile
        else:
            de_name = "Naigaon Market"
            de_mobile = "9518901902"

        if status == "out_for_delivery":
            try:
                ### testing working good
                with open("./utils/htmlemails/out_for_delivery.html", "r", encoding="utf-8") as file:
                    email_content = file.read()
                    formatted_email = email_content.replace("{name}", name).replace("{tracking_number}", tracking_number).replace("{total_items}", total_items).replace("{tracking_url}", f"https://www.naigaonmarket.com/profile/orders/{order_number}").replace('{unsubscribe_url}', f"https://www.naigaonmarket.com/profile/unsubscribe-email?email={receiver_email}")
                    subject = f"Naigaon Market: #Package{tracking_number} is out for delivery"
                    print("Email sent successfully")
                    # send_mail_thread(subject, subject, settings.EMAIL_HOST_USER, [receiver_email], html=formatted_email)
            except Exception as e:
                print(f"Email send failed: {e}")

            try:
                # content_template_sid = wa_content_templates["delivery_out_sid"]
                # variables = {
                #     'name': name,
                #     'package_number': tracking_number,
                #     'no_of_items': total_items,
                #     'de_name': de_name,
                #     'de_mobile': de_mobile
                # }
                # print("WA message sent!!")
                # send_wa_msg(content_template_sid, variables, mobile)

                variables = [name, tracking_number, total_items, de_name, de_mobile]
                template_name = wa_plivo_templates["delivery_out_sid"]
                print("WA message sent!!")
                send_wa_msg_plivo(template_name, variables, mobile)
            except Exception as e:
                print(f"WhatsApp message send failed: {e}")

        elif status == "delivered":
            
            try:
                ### testing working good
                with open("./utils/htmlemails/delivered.html", "r", encoding="utf-8") as file:
                    email_content = file.read()
                    formatted_email = email_content.replace("{name}", name).replace("{tracking_number}", tracking_number).replace("{total_items}", total_items).replace("{review_url}", f"https://www.naigaonmarket.com/profile/orders/{order_number}").replace('{unsubscribe_url}', f"https://www.naigaonmarket.com/profile/unsubscribe-email?email={receiver_email}")
                    subject = f"Naigaon Market: #Package{tracking_number} delivered successfully"
                    print("Email sent successfully")
                    # send_mail_thread(subject, subject, settings.EMAIL_HOST_USER, [receiver_email], html=formatted_email)
            except Exception as e:
                print(f"Email send failed: {e}")


            try:
                # content_template_sid = wa_content_templates["delivered_sid"]
                # variables = {
                #     'name': name,
                #     'package_number': tracking_number,
                #     'no_of_items': total_items,
                #     'feedback_link': "https://naigaonmarket.com",
                # }
                # print("WA message sent!!")
                # send_wa_msg(content_template_sid, variables, mobile)
                feedback_link = "https://naigaonmarket.com"
                variables = [name, tracking_number, total_items, feedback_link]
                template_name = wa_plivo_templates["delivered_sid"]
                print("WA message sent!!")
                send_wa_msg_plivo(template_name, variables, mobile)
            except Exception as e:
                print(f"WhatsApp message send failed: {e}")

    # Run after the transaction commits
    transaction.on_commit(lambda: threading.Thread(target=delayed_package_notification).start())