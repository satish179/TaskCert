from django.urls import path
from certificates.views import download_certificate

urlpatterns = [
    # ...existing urls...
    path('certificates/download/<str:certificate_id>/', download_certificate, name='download_certificate'),
    path('manage-exams/create/', views.create_exam_view, name='create_exam'),
    path('manage-exams/<int:exam_id>/add-questions/', views.add_questions_view, name='add_questions'),
    path('exams/delete-question/<int:question_id>/', views.delete_question_view, name='delete_question'),
]