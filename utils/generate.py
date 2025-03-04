import uuid

import random
import string
from django.utils.timezone import now


def generate_tracking_number():
    return f"{uuid.uuid4().hex[:8].upper()}"

def generate_otp():
    return str(random.randint(100000, 999999))


def generate_order_number():
    timestamp = now().strftime("%Y%m%d%H")  # Format: YYYYMMDDHHMM
    random_str = ''.join(random.choices(string.digits, k=5))
    return f"{timestamp}-{random_str}"
