from django.db import models

# Create your models here.
from products.models import ProductListing
from users.models import User


class Question(models.Model):
    product_listing = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name="listing_questions")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_questions", null=True,blank=True)
    question_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_answers")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_answers", null=True,blank=True)
    answer_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)