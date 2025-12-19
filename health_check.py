import os
import django
from django.test.client import Client
from django.contrib.auth import get_user_model
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

User = get_user_model()
client = Client()

def run_checks():
    print("Starting System Health Check...\n")
    results = []
    
    # 1. Check Public Pages
    urls = ['/', '/login/', '/register/']
    for url in urls:
        try:
            resp = client.get(url)
            status = resp.status_code
            if status == 200:
                print(f"[PASS] {url} loaded successfully (200 OK)")
                results.append(True)
            else:
                print(f"[FAIL] {url} returned {status}")
                results.append(False)
        except Exception as e:
            print(f"[ERROR] {url} failed: {e}")
            results.append(False)

    # 2. Check Protected Pages (Login as User)
    print("\nChecking Student Pages (requires login)...")
    try:
        # Create or Get Dummy User
        user, created = User.objects.get_or_create(username='test_student', email='test@student.com')
        if created:
            user.set_password('password123')
            user.role = 'user'
            user.save()
        
        client.force_login(user)
        
        protected_urls = ['/dashboard/', '/exams/', '/certificates/']
        for url in protected_urls:
            resp = client.get(url)
            if resp.status_code == 200:
                print(f"[PASS] {url} loaded (200 OK)")
                results.append(True)
            else:
                print(f"[FAIL] {url} returned {resp.status_code}")
                results.append(False)
                
    except Exception as e:
        print(f"[CRITICAL] Failed to setup student user: {e}")
        results.append(False)

    # 3. Check Admin Pages
    print("\nChecking Admin Pages...")
    try:
        admin, created = User.objects.get_or_create(username='test_admin', email='test@admin.com')
        if created:
            admin.set_password('admin123')
            admin.role = 'admin'
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            
        client.force_login(admin)
        
        admin_urls = ['/admin-dashboard/', '/admin-dashboard/activity-log/', '/manage-exams/']
        for url in admin_urls:
            resp = client.get(url)
            if resp.status_code == 200:
                print(f"[PASS] {url} loaded (200 OK)")
                results.append(True)
            else:
                print(f"[FAIL] {url} returned {resp.status_code}")
                results.append(False)
                
    except Exception as e:
         print(f"[CRITICAL] Failed to setup admin user: {e}")
         results.append(False)

    print("\n" + "="*30)
    if all(results):
        print("✅ ALL CHECKS PASSED. System is healthy.")
    else:
        print("❌ SOME CHECKS FAILED. See logs above.")

if __name__ == "__main__":
    run_checks()
