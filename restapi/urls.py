from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView, UserViewSet, MentorViewSet,
    TaskViewSet, SubmissionViewSet, ExamViewSet, QuestionViewSet,
    ResultViewSet, CertificateViewSet,
    login_view, register_view, mentor_register_view, dashboard_view, logout_view, exams_view, certificates_view,
    my_tasks_view, submissions_view, admin_dashboard_view, manage_users_view,
    manage_tasks_view, manage_submissions_view, manage_exams_view, manage_certificates_view, profile_view,
    submit_task_view, review_submission_view, assign_tasks_view, mentor_dashboard_view,
    sample_questions_topics_view, sample_questions_view, verify_certificate_view,
    create_exam_view, add_questions_view, delete_question_view,
    edit_exam_view, delete_exam_view, edit_question_view, activity_log_view,
    leaderboard_view, resource_library_view, upload_resource_view,
    leaderboard_view, resource_library_view, upload_resource_view,
    forum_index_view, create_post_view, post_detail_view, take_exam_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'mentors', MentorViewSet, basename='mentor')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'results', ResultViewSet, basename='result')
router.register(r'certificates', CertificateViewSet, basename='certificate')

urlpatterns = [
    # Root landing page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Template-based views - User
    path('login/', login_view, name='login'),
    path('student-login/', RedirectView.as_view(url='/login/?role=student', permanent=False), name='student_login'),
    path('admin-login/', RedirectView.as_view(url='/login/?role=admin', permanent=False), name='admin_login'),
    path('register/', register_view, name='register'),
    # path('mentor-register/', mentor_register_view, name='mentor_register'), # Disabled: Mentors created via Django Admin only
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    
    # Task and Submission specific routes (must come before generic api/ pattern)
    path('tasks/<int:task_id>/submit/', submit_task_view, name='submit_task'),
    path('submissions/<int:submission_id>/review/', review_submission_view, name='review_submission'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('resources/', resource_library_view, name='resource_library'),
    path('resources/upload/', upload_resource_view, name='upload_resource'),
    path('forum/', forum_index_view, name='forum_index'),
    path('forum/create/', create_post_view, name='create_post'),
    path('forum/<int:post_id>/', post_detail_view, name='post_detail'),
    
    # Template-based views - User continued
    path('my-tasks/', my_tasks_view, name='my_tasks'),
    path('submissions/', submissions_view, name='submissions'),
    path('exams/', exams_view, name='exams'),
    path('exam/<int:exam_id>/take/', take_exam_view, name='take_exam'),
    path('certificates/', certificates_view, name='certificates'),
    path('verify-certificate/', verify_certificate_view, name='verify_certificate'),
    path('sample-questions/', sample_questions_topics_view, name='sample_questions_topics'),
    path('sample-questions/<int:topic_id>/', sample_questions_view, name='sample_questions'),
    
    # Template-based views - Admin
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/activity-log/', activity_log_view, name='activity_log'),
    path('mentor-dashboard/', mentor_dashboard_view, name='mentor_dashboard'),
    path('assign-tasks/', assign_tasks_view, name='assign_tasks'),
    path('manage-users/', manage_users_view, name='manage_users'),
    path('manage-tasks/', manage_tasks_view, name='manage_tasks'),
    path('manage-submissions/', manage_submissions_view, name='manage_submissions'),
    path('manage-exams/', manage_exams_view, name='manage_exams'),
    path('manage-exams/create/', create_exam_view, name='create_exam'),
    path('manage-exams/<int:exam_id>/edit/', edit_exam_view, name='edit_exam'),
    path('manage-exams/<int:exam_id>/delete/', delete_exam_view, name='delete_exam'),
    path('manage-exams/<int:exam_id>/add-questions/', add_questions_view, name='add_questions'),
    path('manage-exams/question/<int:question_id>/edit/', edit_question_view, name='edit_question'),
    path('exams/delete-question/<int:question_id>/', delete_question_view, name='delete_question'),
    path('manage-certificates/', manage_certificates_view, name='manage_certificates'),

    
    # API views (catch-all patterns come last)
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/', include(router.urls)),
]
