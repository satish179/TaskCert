#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Task, CustomUser

# Check task 6
try:
    task = Task.objects.get(id=6)
    print(f"Task 6 found: {task.name}")
    print(f"Assigned to: {task.assigned_to.username if task.assigned_to else 'None'}")
except Task.DoesNotExist:
    print("Task 6 does not exist")

# List all tasks with assignments
print("\n=== ALL TASKS ===")
for task in Task.objects.all():
    print(f"ID {task.id}: {task.name} -> {task.assigned_to.username if task.assigned_to else 'Unassigned'}")

# Check user1
try:
    user1 = CustomUser.objects.get(username='user1')
    print(f"\n=== user1 TASKS ===")
    user_tasks = Task.objects.filter(assigned_to=user1)
    print(f"Total: {user_tasks.count()}")
    for task in user_tasks:
        print(f"ID {task.id}: {task.name}")
except CustomUser.DoesNotExist:
    print("user1 does not exist")
