from ninja import  Router, Query

# router.py
from .models import Address


from .schemas import AddressCreateSchema, AddressOutSchema, AddressUpdateSchema

from django.shortcuts import get_object_or_404

from utils.pagination import PaginatedResponseSchema, paginate_queryset

router = Router()

from ninja_jwt.authentication import JWTAuth


############## 1 city ###########################

######################## Address #######################


# Create Address
@router.post("/addresses/", response=AddressOutSchema, auth=JWTAuth())
def create_address(request, payload: AddressCreateSchema):
    address = Address(**payload.dict())
    address.save()
    return address

# Read Addresss (List)
@router.get("/addresses/", response=PaginatedResponseSchema)
def addresses(request,  page: int = 1, page_size: int = 10,  city: str = None, pin:str = None , ordering: str = None,):
    qs = Address.objects.all()


    if city:
        qs = qs.filter(city=city)
    
    if pin:
        qs = qs.filter(pin=pin)
    
    if ordering:
        qs = qs.order_by(ordering)

    return paginate_queryset(request, qs, AddressOutSchema, page, page_size)

# Read Single Address (Retrieve)
@router.get("/addresses/{address_id}/", response=AddressOutSchema)
def retrieve_address(request, address_id: int):
    address = get_object_or_404(Address, id=address_id)
    return address

# Update Address
@router.put("/addresses/{address_id}/", response=AddressOutSchema)
def update_address(request, address_id: int, payload: AddressUpdateSchema):
    address = get_object_or_404(Address, id=address_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(address, attr, value)
    address.save()
    return address

# Delete Address
@router.delete("/addresses/{address_id}/", auth=JWTAuth())
def delete_address(request, address_id: int):
    address = get_object_or_404(Address, id=address_id)
    address.delete()
    return {"success": True}
