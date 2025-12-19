#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

# Check Alice's tasks
alice = User.objects.filter(username='user1').first()
if alice:
    tasks = Task.objects.filter(assigned_to=alice)
    print(f"Alice's tasks ({alice.username}):")
    print(f"Total tasks: {tasks.count()}")
    print(f"Completed: {tasks.filter(status='completed').count()}")
    print(f"In progress: {tasks.filter(status='in_progress').count()}")
    print(f"Pending: {tasks.filter(status='pending').count()}")

    print("\nTask details:")
    for task in tasks:
        print(f"  {task.name}: {task.status}")

    # Check the logic
    user_tasks = Task.objects.filter(assigned_to=alice)
    completed_tasks = user_tasks.filter(status='completed')
    has_completed_all_tasks = user_tasks.exists() and user_tasks.count() == completed_tasks.count()
    print(f"\nLogic check:")
    print(f"  user_tasks.exists(): {user_tasks.exists()}")
    print(f"  user_tasks.count(): {user_tasks.count()}")
    print(f"  completed_tasks.count(): {completed_tasks.count()}")
    print(f"  has_completed_all_tasks: {has_completed_all_tasks}")
else:
    print("Alice (user1) not found")

# Check submissions
from restapi.models import Submission
submissions = Submission.objects.filter(submitted_by=alice)
print(f"\nAlice's submissions: {submissions.count()}")
for sub in submissions:
    print(f"  {sub.task.name}: {sub.status}")

# Check if there are any exams
from restapi.models import Exam
exams = Exam.objects.all()
print(f"\nTotal exams in system: {exams.count()}")
for exam in exams:
    print(f"  {exam.name}")