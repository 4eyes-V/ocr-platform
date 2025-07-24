from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload'),
    path('analyze/<int:doc_id>/', views.analyze_document, name='analyze'),
]