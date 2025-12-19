#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Task, CustomUser

# List all tasks with detailed info
print("=== ALL TASKS IN DATABASE ===\n")
for task in Task.objects.all():
    assigned_to = task.assigned_to.username if task.assigned_to else "Not Assigned"
    print(f"Task ID: {task.id}")
    print(f"  Name: {task.name}")
    print(f"  Assigned to: {assigned_to}")
    print(f"  Status: {task.status}")
    print(f"  Due Date: {task.due_date}")
    print()

# Check all users
print("=== ALL USERS ===\n")
for user in CustomUser.objects.all():
    print(f"Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {user.role}")
    print(f"  Is Staff: {user.is_staff}")
    tasks_count = Task.objects.filter(assigned_to=user).count()
    print(f"  Assigned Tasks: {tasks_count}")
    if tasks_count > 0:
        for t in Task.objects.filter(assigned_to=user):
            print(f"    - Task {t.id}: {t.name}")
    print()
