import http.client
import json

from decouple import config

Email = config('SHIPROCKET_EMAIL')
Password = config('SHIPROCKET_PASSWORD')

class ShiprocketAPI:

    def __init__(self):
        self.conn = http.client.HTTPSConnection("apiv2.shiprocket.in")
        self.token = self.get_token()

    def get_token(self):
        payload = json.dumps({
        "email": Email,
        "password": Password
        })
        headers = {
        'Content-Type': 'application/json'
        }
        self.conn.request("POST", "/v1/external/auth/login", payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        # print(data.decode("utf-8"))
        return json.loads(data.decode("utf-8"))['token']

        
    def create_order(self, package):
        
        order = package.order
        items = []

        for package_item in package.package_items.select_related('order_item__product_listing'):
            item = package_item.order_item
            items.append({
                "name": item.product_listing.name,
                "sku": str(item.product_listing.id),
                "units": package_item.quantity,
                "selling_price": float(item.price),
            })


        shipping_address = order.shipping_address

        payload = {
            "order_id": order.order_number,
            "order_date": order.created.strftime("%Y-%m-%d"),
            "pickup_location": "work",  # or static if you don't support dynamic pickups
            "channel_id": "",  # optional
            "billing_customer_name": shipping_address.name.split()[0],
            "billing_last_name": shipping_address.name.split()[1] if len(shipping_address.name.split()) > 1 else "",
            "billing_address": shipping_address.address.line1,
            "billing_city": shipping_address.address.city,
            "billing_pincode": shipping_address.address.pin,
            "billing_state": shipping_address.address.state,
            "billing_country": "India",
            "billing_email": order.user.email,
            "billing_phone": shipping_address.mobile if len(str(shipping_address.mobile)) > 0 else "8888877777",
            "shipping_is_billing": True,
            "order_items": items,
            "payment_method": "Prepaid" if order.payment_status == "completed" else "COD",
            "sub_total": float(order.total_amount),
            "length": 10,
            "breadth": 10,
            "height": 10,
            "weight": 1,
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            'Content-Type': 'application/json',
        }

        json_payload = json.dumps(payload).encode('utf-8')

        self.conn.request("POST", "/v1/external/orders/create/adhoc", json_payload, headers)
        res = self.conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))