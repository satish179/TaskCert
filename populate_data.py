#!/usr/bin/env python
import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Mentor, Task, Exam, Question
from django.contrib.auth import get_user_model

User = get_user_model()

# Create Mentors
mentors_data = [
    {
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'bio': 'Experienced Python and Django developer with 10 years of experience',
        'specialization': 'Web Development'
    },
    {
        'name': 'Sarah Johnson',
        'email': 'sarah.johnson@example.com',
        'bio': 'Expert in cloud architecture and DevOps',
        'specialization': 'Cloud & DevOps'
    },
]

for mentor_data in mentors_data:
    mentor, created = Mentor.objects.get_or_create(
        email=mentor_data['email'],
        defaults={
            'name': mentor_data['name'],
            'bio': mentor_data['bio'],
            'specialization': mentor_data['specialization']
        }
    )
    if created:
        print(f"Created mentor: {mentor.name}")

# Create sample users
user1, created = User.objects.get_or_create(
    username='user1',
    defaults={
        'email': 'user1@example.com',
        'first_name': 'Alice',
        'last_name': 'Developer',
        'role': 'user',
        'mentor': Mentor.objects.first()
    }
)
if created:
    user1.set_password('user123')
    user1.save()
    print(f"Created user: {user1.username}")

user2, created = User.objects.get_or_create(
    username='user2',
    defaults={
        'email': 'user2@example.com',
        'first_name': 'Bob',
        'last_name': 'Coder',
        'role': 'user',
        'mentor': Mentor.objects.first()
    }
)
if created:
    user2.set_password('user123')
    user2.save()
    print(f"Created user: {user2.username}")

# Create Tasks
mentor = Mentor.objects.first()
user = User.objects.filter(role='user').first()

if user:
    tasks_data = [
        {
            'name': 'Create Login Functionality',
            'remarks': 'Implement user login with email and password',
            'days_from_now': 7
        },
        {
            'name': 'Create Registration Page',
            'remarks': 'Build user registration form with validation',
            'days_from_now': 14
        },
        {
            'name': 'Implement Dashboard',
            'remarks': 'Create user dashboard with task overview',
            'days_from_now': 21
        },
        {
            'name': 'Add Task Submission Feature',
            'remarks': 'Allow users to submit completed tasks',
            'days_from_now': 28
        },
    ]

    for task_data in tasks_data:
        due_date = timezone.now() + timedelta(days=task_data['days_from_now'])
        task, created = Task.objects.get_or_create(
            name=task_data['name'],
            assigned_by=mentor,
            assigned_to=user,
            defaults={
                'remarks': task_data['remarks'],
                'due_date': due_date,
                'status': 'pending'
            }
        )
        if created:
            print(f"Created task: {task.name}")

# Create Exam
exam, created = Exam.objects.get_or_create(
    name='Django Fundamentals Exam',
    created_by=mentor,
    defaults={
        'description': 'Test your knowledge of Django web framework basics',
        'due_date': timezone.now() + timedelta(days=30),
        'assigned_to': user
    }
)
if created:
    print(f"Created exam: {exam.name}")

# Create Questions
questions_data = [
    {
        'question_text': 'What does MVT stand for in Django?',
        'options': ['Model View Template', 'Model Viewer Team', 'Multi View Technology', 'Modular Visualization Tool'],
        'correct_answer': 'Model View Template'
    },
    {
        'question_text': 'Which file is used to configure Django settings?',
        'options': ['config.py', 'settings.py', 'django.py', 'app.py'],
        'correct_answer': 'settings.py'
    },
    {
        'question_text': 'What is the ORM in Django called?',
        'options': ['Django ORM', 'QuerySet', 'Model', 'Database'],
        'correct_answer': 'QuerySet'
    },
    {
        'question_text': 'Which command creates a new Django project?',
        'options': ['python manage.py create', 'django-admin startproject', 'python django.py init', 'create-django-project'],
        'correct_answer': 'django-admin startproject'
    },
    {
        'question_text': 'What is the URL routing mechanism in Django called?',
        'options': ['URLPatterns', 'Routes', 'Paths', 'Links'],
        'correct_answer': 'URLPatterns'
    },
]

for q_data in questions_data:
    question, created = Question.objects.get_or_create(
        question_text=q_data['question_text'],
        exam=exam,
        defaults={
            'options': q_data['options'],
            'correct_answer': q_data['correct_answer'],
            'question_type': 'multiple_choice'
        }
    )
    if created:
        print(f"Created question: {question.question_text[:50]}...")

print("\nSample data created successfully!")
