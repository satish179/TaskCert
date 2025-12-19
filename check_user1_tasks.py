#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Task, Submission, CustomUser

user = CustomUser.objects.get(username='user1')
tasks = Task.objects.filter(assigned_to=user).order_by('created_at')

print("user1 Tasks:\n")
for i, task in enumerate(tasks, 1):
    submissions = Submission.objects.filter(task=task)
    print(f"{i}. {task.name}")
    print(f"   Status: {task.status}")
    print(f"   Due: {task.due_date}")
    if submissions:
        print(f"   Submission: {submissions.first().status}")
    print()
