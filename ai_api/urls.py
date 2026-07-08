from django.urls import path
from . import views

urlpatterns = [
    path('process-ai/', views.process_ai, name='process_ai'),
]