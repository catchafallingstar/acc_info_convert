from django.urls import path
from . import views

urlpatterns = [
    path('process-ai/', views.process_ai, name='process_ai'),
    path('api/generate-pdf/', views.generate_accessible_pdf, name='generate_pdf'),
]