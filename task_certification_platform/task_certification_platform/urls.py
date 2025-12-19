"""
URL configuration for task_certification_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # User authentication
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls', namespace='users')),
    
    # Task management
    path('tasks/', include('tasks.urls', namespace='tasks')),
    
    # Exams
    path('exams/', include('exams.urls', namespace='exams')),
    
    # Certificates
    path('certificates/', include('certificates.urls', namespace='certificates')),
    
    # API
    path('api/', include('api.urls', namespace='api')),
    
    # REST Framework auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Add debug toolbar if in development
if settings.DEBUG:
    try:
        import debug_toolbar
    except Exception:
        debug_toolbar = None

    if debug_toolbar is not None:
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler400 = 'task_certification_platform.views.bad_request'
handler403 = 'task_certification_platform.views.permission_denied'
handler404 = 'task_certification_platform.views.page_not_found'
handler500 = 'task_certification_platform.views.server_error'
