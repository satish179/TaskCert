#!/usr/bin/env python


def main() -> None:
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
    django.setup()

    from restapi.models import Task, Submission
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Get user1
    user = User.objects.filter(username='user1').first()
    if not user:
        print("User user1 not found")
        return

    # Get first pending task
    task = Task.objects.filter(assigned_to=user, status='pending').first()
    if not task:
        print("No pending tasks for user1")
        return

    print(f"Submitting task: {task.name} for user: {user.username}")

    # Create submission
    submission = Submission.objects.create(
        task=task,
        submitted_by=user,
        content="Test submission content",
        status='submitted'
    )

    # Update task status
    task.status = 'in_progress'
    task.save()

    print(f"Submission created: {submission.id}")
    print(f"Task status updated to: {task.status}")

    # Check if admin can approve
    admin = User.objects.filter(username='admin').first()
    if admin:
        print(f"Admin found: {admin.username}, is_staff: {admin.is_staff}")
    else:
        print("Admin not found")


if __name__ == '__main__':
    main()