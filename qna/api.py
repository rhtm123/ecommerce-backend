from ninja import  Router, Query

# router.py
from .models import Question, Answer
from .schemas import ( 
    QuestionCreateSchema, QuestionOutSchema, QuestionUpdateSchema,
    AnswerOutSchema, AnswerUpdateSchema, AnswerCreateSchema
)
from django.shortcuts import get_object_or_404
from utils.pagination import PaginatedResponseSchema, paginate_queryset

from ninja_jwt.authentication import JWTAuth

from utils.cache import cache_response


router = Router()



############################ Question ############################
@router.post("/questions/", response=QuestionOutSchema,auth=JWTAuth())
def create_question(request, payload: QuestionCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)
    question = Question(**payload.dict())
        
    question.save()
    return question

# Read Questions (List)

@router.get("/questions/", response=PaginatedResponseSchema)
@cache_response()
def questions(request,  
              page: int = 1, 
              page_size: int = 10, 
              product_listing_id:str = None ,
              answers_required: bool = False,
              ordering: str = None,):
    qs = Question.objects.all()


    query = ""


    if product_listing_id:
        qs = qs.filter(product_listing__id=product_listing_id)
        query = query + "&product_listing_id=" + str(product_listing_id)


    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + str(ordering)


    # Fetch answers for each question
    if answers_required:
        for question in qs:
            question.answers = Answer.objects.filter(question=question)
        query = query + "&answers_required=" + str(answers_required)

        

    return paginate_queryset(request, qs, QuestionOutSchema, page, page_size, query)

# Read Single Question (Retrieve)
@router.get("/questions/{question_id}/", response=QuestionOutSchema)
def retrieve_question(request, question_id: int, answers_required: bool = False,):
    question = get_object_or_404(Question, id=question_id)
    if answers_required:
        question.answers = Answer.objects.filter(question=question)
    return question

# Update Question
@router.put("/questions/{question_id}/", response=QuestionOutSchema)
def update_question(request, 
                    question_id: int, 
                    payload: QuestionUpdateSchema,
                    ):
    question = get_object_or_404(Question, id=question_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(question, attr, value)
    question.save()
    return question

# Delete Question
@router.delete("/questions/{question_id}/")
def delete_question(request, question_id: int):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return {"success": True}



############################ Answer ############################
@router.post("/answers/", response=AnswerOutSchema)
def create_answer(request, payload: AnswerCreateSchema):

    # locality = get_object_or_404(Locality, id=payload.locality_id)
    answer = Answer(**payload.dict())
        
    answer.save()
    return answer

# Read Answers (List)
@router.get("/answers/", response=PaginatedResponseSchema)
def answers(request,  page: int = 1, page_size: int = 10, question_id:str = None , ordering: str = None,):
    qs = Answer.objects.all()


    query = ""


    if question_id:
        qs = qs.filter(question__id=question_id)
        query = query + "&question_id=" + str(question_id)


    if ordering:
        qs = qs.order_by(ordering)
        query = query + "&ordering=" + str(ordering)


    return paginate_queryset(request, qs, AnswerOutSchema, page, page_size, query)

# Read Single Answer (Retrieve)
@router.get("/answers/{answer_id}/", response=AnswerOutSchema)
def retrieve_answer(request, answer_id: int):
    answer = get_object_or_404(Answer, id=answer_id)
    return answer

# Update Answer
@router.put("/answers/{answer_id}/", response=AnswerOutSchema)
def update_answer(request, answer_id: int, payload: AnswerUpdateSchema):
    answer = get_object_or_404(Answer, id=answer_id)
    for attr, value in payload.dict().items():
        if value is not None:
            setattr(answer, attr, value)
    answer.save()
    return answer

# Delete Answer
@router.delete("/answers/{answer_id}/")
def delete_answer(request, answer_id: int):
    answer = get_object_or_404(Answer, id=answer_id)
    answer.delete()
    return {"success": True}


