from django.contrib import admin
from .models import ExamResult, Certificate

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'passed', 'created_at')
    list_filter = ('passed', 'created_at')
    search_fields = ('user__username', 'exam')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'institution_name', 'certificate_id', 'created_at')
    search_fields = ('user__username', 'exam', 'certificate_id')