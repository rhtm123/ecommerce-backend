from ninja import Schema
from datetime import date
from typing import Optional

from .models import Advertisement



class AdvertisementOutSchema(Schema):
    estore_id: Optional[int] = None
    id: int
    title: str
    image: Optional[str] = None
    link: str | None
    start_date: date
    end_date: date
    is_active: bool

    @staticmethod
    def resolve_image(obj: Advertisement) -> Optional[str]:
        try:
            # print(obj.main_image)
            # print(obj.main_image.url)
            return obj.image.url if obj.image else None
        except:
            return None 
