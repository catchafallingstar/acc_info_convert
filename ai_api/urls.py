from django.urls import path
from . import views

urlpatterns = [
   # Resolves to /api/process-ai/
    path('process-ai/', views.process_ai, name='process_ai'),
    
    # Resolves to /api/generate-accessible-pdf/
    path('generate-accessible-pdf/', views.generate_accessible_pdf, name='generate_accessible_pdf'),
    path('process-pdf-ai/', views.process_pdf_ai, name='process_pdf_ai'),
]