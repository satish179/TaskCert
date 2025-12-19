from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Mentor, Task, Submission, Exam, Question, Result, Certificate, CustomUser, Topic, SampleQuestion, ExamAttempt

User = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Platform', {'fields': ('role', 'mentor', 'certificate_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Platform', {'fields': ('role', 'mentor')}),
    )

class MentorAdminForm(forms.ModelForm):
    username = forms.CharField(required=False, help_text='Username for the mentor login account')
    password1 = forms.CharField(required=False, widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(required=False, widget=forms.PasswordInput, label='Confirm password')

    class Meta:
        model = Mentor
        fields = ('name', 'email', 'specialization', 'bio')

    def clean(self):
        cleaned = super().clean()
        is_creating = self.instance is None or self.instance.pk is None

        username = (cleaned.get('username') or '').strip()
        password1 = cleaned.get('password1') or ''
        password2 = cleaned.get('password2') or ''

        if is_creating:
            if not username:
                raise ValidationError({'username': 'Username is required.'})
            if not password1:
                raise ValidationError({'password1': 'Password is required.'})
            if password1 != password2:
                raise ValidationError({'password2': 'Passwords do not match.'})
            if User.objects.filter(username=username).exists():
                raise ValidationError({'username': 'This username already exists.'})

        return cleaned


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    form = MentorAdminForm
    list_display = ('name', 'email', 'specialization', 'mentor_username')
    search_fields = ('name', 'email', 'user__username')
    readonly_fields = ('user',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Hide login fields on edit; use the CustomUser admin to change username/password later.
        if obj is not None:
            for field_name in ('username', 'password1', 'password2'):
                if field_name in form.base_fields:
                    form.base_fields.pop(field_name)
        return form

    def mentor_username(self, obj):
        return obj.user.username if getattr(obj, 'user', None) else '-'
    mentor_username.short_description = 'Username'

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)

            if not change and not obj.user:
                username = (form.cleaned_data.get('username') or '').strip()
                password = form.cleaned_data.get('password1') or ''

                first = (obj.name or '').split(' ')[0] if obj.name else ''
                last = ' '.join((obj.name or '').split(' ')[1:]) if obj.name and len((obj.name or '').split(' ')) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    email=obj.email,
                    password=password,
                    first_name=first,
                    last_name=last,
                    role='admin',
                    is_staff=True,
                    is_superuser=False,
                )

                # Keep compatibility: mentor accounts point to their own mentor profile.
                user.mentor = obj
                user.save(update_fields=['mentor'])

                obj.user = user
                obj.save(update_fields=['user'])

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_to', 'assigned_by', 'status', 'due_date')
    list_filter = ('status', 'due_date')
    search_fields = ('name', 'assigned_to__username', 'assigned_by__name')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'submitted_by', 'status', 'score', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('task__name', 'submitted_by__username')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'assigned_to', 'due_date', 'duration_minutes', 'pass_score', 'max_attempts')
    search_fields = ('name', 'created_by__name', 'assigned_to__username')
    list_filter = ('created_by', 'assigned_to', 'due_date')


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'attempt_number', 'status', 'score', 'passed', 'started_at', 'submitted_at', 'expires_at')
    list_filter = ('status', 'passed', 'exam')
    search_fields = ('user__username', 'exam__name')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'exam', 'question_type', 'correct_answer')
    list_filter = ('question_type', 'exam')
    search_fields = ('question_text', 'exam__name')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'score', 'passed', 'taken_at')
    list_filter = ('passed', 'taken_at', 'exam')
    search_fields = ('user__username', 'exam__name')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'certificate_number', 'name', 'institution', 'score', 'issued_date')
    search_fields = ('user__username', 'exam__name', 'certificate_number', 'name')
    list_filter = ('issued_date', 'exam')
    fields = ('user', 'exam', 'certificate_number', 'name', 'institution', 'score')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'name': ('name',)}

@admin.register(SampleQuestion)
class SampleQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'topic', 'question_type', 'difficulty_level', 'is_active', 'created_at')
    list_filter = ('question_type', 'difficulty_level', 'is_active', 'topic', 'created_at')
    search_fields = ('question_text', 'topic__name', 'correct_answer')
    raw_id_fields = ('topic',)
    fieldsets = (
        ('Question Details', {
            'fields': ('topic', 'question_text', 'question_type', 'difficulty_level')
        }),
        ('Answer Options', {
            'fields': ('options', 'correct_answer', 'explanation'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        })
    )
