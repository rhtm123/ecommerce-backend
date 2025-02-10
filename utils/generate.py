import uuid

import random
import string
from django.utils.timezone import now


def generate_tracking_number():
    return f"TR-{uuid.uuid4().hex[:8].upper()}"



def generate_order_number():
    timestamp = now().strftime("%Y%m%d%H%M")  # Format: YYYYMMDDHHMM
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"OR-{timestamp}-{random_str}"
