"""
Views for the task_certification_platform project.
"""
from django.shortcuts import render
from django.views import View
from django.views.defaults import (
    page_not_found as django_page_not_found,
    server_error as django_server_error,
    bad_request as django_bad_request,
    permission_denied as django_permission_denied,
)
from django.template.loader import get_template
from django.http import HttpResponse, Http404

class HomeView(View):
    """Home page view."""
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        context = {
            'title': 'Welcome to Task Certification Platform',
        }
        return render(request, self.template_name, context)

def custom_error_view(request, template_name, status_code, error_message=None):
    """
    Render a custom error page.
    """
    context = {
        'status_code': status_code,
        'error_message': error_message or 'An error occurred',
    }
    return render(request, template_name, context, status=status_code)

def bad_request(request, exception, template_name='errors/400.html'):
    """
    Custom 400 error handler.
    """
    return custom_error_view(
        request,
        template_name,
        400,
        'Bad Request. The request could not be understood or was missing required parameters.'
    )

def permission_denied(request, exception, template_name='errors/403.html'):
    """
    Custom 403 error handler.
    """
    return custom_error_view(
        request,
        template_name,
        403,
        'Permission Denied. You do not have permission to access this page.'
    )

def page_not_found(request, exception, template_name='errors/404.html'):
    """
    Custom 404 error handler.
    """
    return custom_error_view(
        request,
        template_name,
        404,
        'Page Not Found. The requested page could not be found.'
    )

def server_error(request, template_name='errors/500.html'):
    """
    Custom 500 error handler.
    """
    return custom_error_view(
        request,
        template_name,
        500,
        'Server Error. An unexpected error occurred on the server.'
    )

# Fallback to Django's default error handlers if custom templates don't exist
try:
    from django.template.loader import get_template
    # Check if custom error templates exist
    if not get_template('errors/400.html'):
        bad_request = django_bad_request
    if not get_template('errors/403.html'):
        permission_denied = django_permission_denied
    if not get_template('errors/404.html'):
        page_not_found = django_page_not_found
    if not get_template('errors/500.html'):
        server_error = django_server_error
except Exception:
    # If there's any error loading templates, use Django's default handlers
    bad_request = django_bad_request
    permission_denied = django_permission_denied
    page_not_found = django_page_not_found
    server_error = django_server_error
