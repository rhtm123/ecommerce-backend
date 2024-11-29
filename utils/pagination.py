from django.core.paginator import Paginator
from ninja import Query
from pydantic import BaseModel
from typing import List, Optional, Type, TypeVar

# Define a type variable for the schema
T = TypeVar('T', bound=BaseModel)

class PaginatedResponseSchema(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[T]

    class Config:
        arbitrary_types_allowed = True

def paginate_queryset(request, queryset, schema: Type[T], page_number: int = 1, page_size: int = 10):
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)

    # Build the base URL without query parameters
    base_url = request.build_absolute_uri(request.path)

    if base_url.startswith('http://'):
        base_url = base_url.replace('http://', 'https://', 1)
        
    next_url = f"{base_url}?page={page_obj.next_page_number()}" if page_obj.has_next() else None
    previous_url = f"{base_url}?page={page_obj.previous_page_number()}" if page_obj.has_previous() else None

    # Convert queryset to list of dictionaries
    results = [schema.from_orm(obj) for obj in page_obj.object_list]

    return PaginatedResponseSchema(
        count=paginator.count,
        next=next_url,
        previous=previous_url,
        results=results
    )
