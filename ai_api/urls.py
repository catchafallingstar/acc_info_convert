from django.urls import path
from . import views

urlpatterns = [
   # Resolves to /api/process-ai/
    path('process-ai/', views.process_ai, name='process_ai'),
    
    # Resolves to /api/generate-pdf/
    path('generate-pdf/', views.generate_accessible_pdf, name='generate_pdf'),
]