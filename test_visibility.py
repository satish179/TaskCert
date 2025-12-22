import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import CustomUser, Task, Mentor

def test_visibility():
    print("--- Testing Task Visibility Logic ---")
    
    # 1. Setup Data
    user, _ = CustomUser.objects.get_or_create(username='vis_student', defaults={'role': 'user'})
    mentor, _ = Mentor.objects.get_or_create(name='Test Mentor', email='tm@e.com')
    
    # Clear existing tasks
    Task.objects.filter(assigned_to=user).delete()
    
    t1 = Task.objects.create(name='Task 1', status='pending', due_date='2030-01-01', assigned_by=mentor, assigned_to=user)
    t2 = Task.objects.create(name='Task 2', status='pending', due_date='2030-01-02', assigned_by=mentor, assigned_to=user)
    print(f"Created 2 pending tasks: {t1.name}, {t2.name}")
    
    # 2. Simulate Dashboard Query (The NEW logic)
    print("\n[Scenario A] 2 Pending Tasks")
    visible_tasks = Task.objects.filter(
        assigned_to=user, 
        status__in=['pending', 'in_progress']
    ).order_by('due_date', 'created_at')
    
    count = visible_tasks.count()
    print(f"Visible Tasks: {count}")
    for t in visible_tasks:
        print(f" - {t.name} ({t.status})")
        
    if count == 2:
        print("✅ SUCCESS: Student sees all pending tasks.")
    else:
        print("❌ FAILURE: Student should see 2 tasks.")

    # 3. Scenario B: One In-Progress, One Pending
    print("\n[Scenario B] Task 1 In-Progress")
    t1.status = 'in_progress'
    t1.save()
    
    visible_tasks = Task.objects.filter(
        assigned_to=user, 
        status__in=['pending', 'in_progress']
    ).order_by('due_date', 'created_at')
    
    count = visible_tasks.count()
    print(f"Visible Tasks: {count}")
    for t in visible_tasks:
        print(f" - {t.name} ({t.status})")

    if count == 2:
         print("✅ SUCCESS: Student sees both In-Progress and Pending tasks.")
    else:
         print(f"❌ FAILURE: Logic hidden pending task? (Old logic would show only 1)")

if __name__ == '__main__':
    test_visibility()
