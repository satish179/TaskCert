"""
Context processors for the task_certification_platform project.
"""
from django.conf import settings

def site_info(request):
    """
    Add site information to the template context.
    """
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Task Certification Platform'),
        'SITE_DOMAIN': getattr(settings, 'SITE_DOMAIN', 'localhost:8000'),
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'DEBUG': settings.DEBUG,
    }
