from django.contrib import admin

# Register your models here.

from .models import Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline,] 