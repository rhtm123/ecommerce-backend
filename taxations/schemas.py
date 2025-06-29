from ninja import Schema
from datetime import datetime
from typing import Optional

class TaxCategoryOutSchema(Schema):
    id: int
    name: str
    details: Optional[str] = None
    cgst_rate: float
    sgst_rate: float
    igst_rate: float
    created: datetime
    updated: datetime

class TaxCategoryCreateSchema(Schema):
    name: str
    details: Optional[str] = None
    cgst_rate: float
    sgst_rate: float

class TaxCategoryUpdateSchema(Schema):
    name: Optional[str] = None
    details: Optional[str] = None
    cgst_rate: Optional[float] = None
    sgst_rate: Optional[float] = None
