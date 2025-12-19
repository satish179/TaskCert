#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Task, Submission, CustomUser

user = CustomUser.objects.get(username='user1')
task = Task.objects.get(name='Add Task Submission Feature', assigned_to=user)

print(f"Current task status: {task.status}\n")

# Create a submission
submission = Submission.objects.create(
    task=task,
    submitted_by=user,
    content="Completed the task submission feature implementation.",
    status='submitted'
)

# Update task status
task.status = 'in_progress'
task.save()

print(f"Submission created: {submission.id}")
print(f"Task status updated to: {task.status}\n")

# Now approve it as admin
submission.status = 'approved'
submission.score = 100
submission.remarks = "Excellent work!"
submission.save()

task.status = 'completed'
task.save()

print(f"Submission approved!")
print(f"Task status updated to: {task.status}\n")

# Check all tasks completed
all_tasks = Task.objects.filter(assigned_to=user)
completed = all_tasks.filter(status='completed').count()
print(f"user1 Progress: {completed}/{all_tasks.count()} tasks completed")

if completed == all_tasks.count():
    print("\n✅ ALL TASKS COMPLETED! User can now access exams.")
