from django.urls import path
from versions import views

urlpatterns = [
    path('versions/', views.VersionListCreate.as_view()),
    path('version/<int:pk>/', views.VersionGetUpdate.as_view()),
    path('version/<str:slug>/', views.VersionGetUpdateSlug.as_view()),
    path('version/delete/<int:pk>/', views.VersionDelete.as_view()),
]