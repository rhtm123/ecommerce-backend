

from datetime import datetime
from typing import Optional, List
from ninja import Schema
from ninja.schema import Field

from users.schemas import UserOutSchema


class QuestionOutSchema(Schema):
    id: int
    question_text: str
    user: Optional[UserOutSchema] = None
    product_listing_id: int

    
    created: datetime
    updated: datetime

class QuestionCreateSchema(Schema):
    question_text: str
    user_id: Optional[int] = None
    product_listing_id: int

 
class QuestionUpdateSchema(Schema):
    question_text: Optional[str] = None


class AnswerOutSchema(Schema):
    id: int
    answer_text: str
    user_id: Optional[int] = None
    question_id: Optional[int] = None
    
    created: datetime
    updated: datetime

class AnswerCreateSchema(Schema):
    answer_text: str
    user_id: Optional[int] = None
    question_id: Optional[int] = None


 
class AnswerUpdateSchema(Schema):
    answer_text: Optional[str] = None

