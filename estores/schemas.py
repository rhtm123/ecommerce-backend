# from datetime import datetime
from typing import Optional
from ninja import Schema
# from ninja.schema import Field

from locations.schemas import AddressOutSchema

from .models import EStore

class EStoreOutSchema(Schema):
    id: int
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    social_accounts: Optional[dict] = None
    website: Optional[str] = None
    address: Optional[AddressOutSchema] = None  # Assuming Address is a foreign key
    # created: str  # Use str to represent datetime in ISO format
    # updated: str  # Use str to represent datetime in ISO format

    icon: Optional[str] = None
    favicon: Optional[str] = None

    @staticmethod
    def resolve_icon(obj: EStore) -> Optional[str]:
        """
        Resolves the URL for the main image.
        """
        try:
            # print(obj.main_image)
            # print(obj.main_image.url)
            return obj.icon.url if obj.icon else None
        except:
            return None
        
    @staticmethod
    def resolve_logo(obj: EStore) -> Optional[str]:
        """
        Resolves the URL for the logo image.
        """
        try:
            return obj.logo.url if obj.logo else None
        except:
            return None
        
    @staticmethod
    def resolve_favicon(obj: EStore) -> Optional[str]:  
        """
        Resolves the URL for the favicon image.
        """
        try:
            return obj.favicon.url if obj.favicon else None
        except:
            return None


class WebPageOutSchema(Schema):
    id: int
    estore_id: Optional[int] = None
    name: str
    content: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None



class DeliveryPinOutSchema(Schema):
    id: int
    pin_code: Optional[str] = None
    estore_id: Optional[int] = None
    cod_available: bool
    city: Optional[str] = None
    state: Optional[str] = None