
from ninja import Schema
from typing import Optional, List
from datetime import datetime  # Import datetime

from .models import Blog, Tag

from users.schemas import UserOutSchema

# from .models import Category

from products.schemas import CategoryOutSchema



class TagOutSchema(Schema):
    id: int
    slug: str
    name: str

    estore_id: Optional[int] = None

    created: datetime
    updated: datetime



# class BlogInSchema(Schema):
#     id: int  # Optional for output, required for update
#     title: str
#     seo_title: str = None
#     seo_description: str = None
#     content: str
#     is_published: bool
#     img: Optional[str] = None  # URL path to the image
#     # author: int  # Foreign key ID (consider using a separate UserSchema for detail)
#     views: int
#     read_time: int  # Minutes
#     likes: int
#     dislikes: int
#     # tags: List[TagSchema] = []  # List of nested Tag schemas

#     class Config:
#         model = Blog
#         # model_fields = '__all__'  # Or explicitly list desired fields

class BlogOutSchema(Schema):
    id: int  # Optional for output, required for update
    title: str
    category: Optional[CategoryOutSchema] = None # Uncomment if you add a Category model
    seo_title: str = None
    seo_description: str = None
    content: str
    slug: str = None  # Optional field (derived from title)
    is_published: bool
    img: Optional[str] = None  # URL path to the image
    author: UserOutSchema  # Use the UserSchema for author details

    # author: int  # Foreign key ID (consider using a separate UserSchema for detail)
    views: int
    read_time: int  # Minutes
    likes: int
    dislikes: int
    tags: List[TagOutSchema] = []  # List of nested Tag schemas
    created: datetime
    updated: datetime

    @staticmethod
    def resolve_img(obj: Blog) -> Optional[str]:
        """
        Resolves the URL for the main image.
        """
        try:
            return obj.img.url if obj.img else None
        except:
            return None

    class Config:
        model = Blog
        model_fields = '__all__'  # Or explicitly list desired fields