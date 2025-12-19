#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import CustomUser, Mentor, Task, Exam, Question, Submission, Certificate
from django.utils import timezone
from datetime import timedelta

# Check existing tasks
print("=== EXISTING TASKS ===")
for task in Task.objects.all():
    print(f"Task ID {task.id}: {task.name} (assigned_to: {task.assigned_to.username if task.assigned_to else 'None'})")

print(f"\nTotal tasks: {Task.objects.count()}")

# Check users
print("\n=== EXISTING USERS ===")
for user in CustomUser.objects.all():
    print(f"User: {user.username} (role: {user.role})")

# If no tasks exist, create sample data
if Task.objects.count() == 0:
    print("\n=== CREATING SAMPLE DATA ===")
    
    # Get or create user1
    user1, created = CustomUser.objects.get_or_create(
        username='user1',
        defaults={
            'email': 'user1@example.com',
            'role': 'user',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    )
    if created:
        user1.set_password('user123')
        user1.save()
        print(f"✓ Created user: {user1.username}")
    else:
        print(f"✓ User exists: {user1.username}")
    
    # Get or create mentor
    mentor, created = Mentor.objects.get_or_create(
        name='Mentor One',
        defaults={'expertise': 'General'}
    )
    if created:
        print(f"✓ Created mentor: {mentor.name}")
    else:
        print(f"✓ Mentor exists: {mentor.name}")
    
    # Create tasks
    tasks_data = [
        {
            'name': 'Python Basics',
            'remarks': 'Learn Python fundamentals including variables, data types, and control flow.',
            'days_to_add': 7
        },
        {
            'name': 'Web Development with Django',
            'remarks': 'Build a simple Django web application with models and views.',
            'days_to_add': 10
        },
        {
            'name': 'Database Design',
            'remarks': 'Design a relational database schema and create migrations.',
            'days_to_add': 5
        },
        {
            'name': 'REST API Development',
            'remarks': 'Create a RESTful API with proper error handling and authentication.',
            'days_to_add': 12
        },
    ]
    
    for task_data in tasks_data:
        task = Task.objects.create(
            name=task_data['name'],
            remarks=task_data['remarks'],
            assigned_to=user1,
            assigned_by=mentor,
            due_date=timezone.now() + timedelta(days=task_data['days_to_add']),
            status='pending'
        )
        print(f"✓ Created task ID {task.id}: {task.name}")
    
    print("\n=== SAMPLE DATA CREATED ===")
    print(f"User: user1 (password: user123)")
    print(f"Tasks created: {Task.objects.count()}")
    
    # Display task list
    print("\n=== TASK LIST FOR user1 ===")
    for task in Task.objects.filter(assigned_to=user1):
        print(f"Task ID {task.id}: {task.name}")
