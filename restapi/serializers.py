from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from .models import Mentor, Task, Submission, Exam, Question, Result, Certificate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'mentor']
        read_only_fields = ['id', 'mentor']

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        username = (validated_data.get('username') or '').strip()
        first_name = (validated_data.get('first_name') or '').strip()
        last_name = (validated_data.get('last_name') or '').strip()

        if not username:
            base = slugify(f"{first_name}{last_name}") or slugify(first_name) or slugify(last_name) or 'user'
            base = base.replace('-', '')
            candidate = base
            counter = 2
            while User.objects.filter(username=candidate).exists():
                candidate = f"{base}{counter}"
                counter += 1
            validated_data['username'] = candidate
        else:
            cleaned = (slugify(username) or '').replace('-', '')
            if not cleaned:
                base = slugify(f"{first_name}{last_name}") or slugify(first_name) or slugify(last_name) or 'user'
                base = base.replace('-', '')
                cleaned = base

            if User.objects.filter(username=cleaned).exists():
                raise serializers.ValidationError({'username': 'Username already exists'})
            validated_data['username'] = cleaned

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            role='user'
        )
        # Mentor is assigned by admin/staff later.
        return user

class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentor
        fields = ['id', 'name', 'email', 'bio', 'specialization', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'due_date', 'remarks', 'status', 'assigned_by', 'assigned_to', 'created_at']

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'task', 'submitted_by', 'submitted_at', 'content', 'status', 'remarks', 'score']

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name', 'description', 'due_date', 'duration_minutes', 'pass_score', 'max_attempts', 'created_by', 'assigned_to', 'created_at']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'exam', 'question_text', 'question_type', 'options', 'correct_answer']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'user', 'exam', 'score', 'passed', 'taken_at']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'user', 'exam', 'issued_date', 'certificate_number', 'name', 'institution', 'score']
