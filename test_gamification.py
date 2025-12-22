import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import CustomUser, Task, Submission, Mentor
from restapi.gamification import award_points

def test_gamification():
    print("--- Testing Gamification System ---")
    
    # 1. Get or Create Test User
    user, _ = CustomUser.objects.get_or_create(username='test_gamer', defaults={'role': 'user'})
    mentor, _ = Mentor.objects.get_or_create(name='Test Mentor', email='tm@e.com')
    user.points = 0 # Reset points
    user.save()
    print(f"1. Test User {user.username} (Points: {user.points})")

    # 2. Assign and Approve a Task (Signal Test)
    print("2. Simulating Task Approval...")
    task = Task.objects.create(name='Game Task', status='pending', due_date='2030-01-01', assigned_by=mentor, assigned_to=user)
    submission = Submission.objects.create(task=task, submitted_by=user, content='Done')
    
    # Approve submission to trigger signal
    submission.status = 'approved'
    submission.save()
    
    user.refresh_from_db()
    print(f"   User Points after Task Approval: {user.points}")
    
    if user.points == 10:
        print("   ✅ SUCCESS: 10 Points awarded for Task!")
    else:
        print(f"   ❌ FAILURE: Expected 10, got {user.points}")

    # 3. Manual Award Test
    print("3. Testing Manual Award...")
    award_points(user, 100, "Manual Bonus")
    user.refresh_from_db()
    print(f"   User Points after Bonus: {user.points}")
    
    if user.points == 110:
         print("   ✅ SUCCESS: Manual points working!")
    else:
         print(f"   ❌ FAILURE: Expected 110, got {user.points}")

if __name__ == '__main__':
    test_gamification()
