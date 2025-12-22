#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Exam, Question, CustomUser
from django.utils import timezone

print("Testing exam input rendering locally...")
print("=" * 60)

# Get a user and exam
try:
    user = CustomUser.objects.filter(is_staff=False).first()
    exam = Exam.objects.first()
    
    if not user:
        print("❌ No non-staff users found. Create a student user first.")
        exit(1)
    
    if not exam:
        print("❌ No exams found. Create an exam first.")
        exit(1)
    
    print(f"✅ User: {user.username}")
    print(f"✅ Exam: {exam.name}")
    print(f"✅ Questions: {exam.questions.count()}")
    
    questions = exam.questions.all()
    for q in questions:
        print(f"\n  Q{q.id}: {q.question_text[:50]}")
        print(f"    Type: {q.question_type}")
        print(f"    Options: {q.options}")
    
    print("\n" + "=" * 60)
    print("✅ Data looks good. Now test the exam page:")
    print("   1. Run: python manage.py runserver")
    print("   2. Login as:", user.username)
    print("   3. Go to /exams/")
    print("   4. Try clicking Start Exam")
    print("   5. Check if you can type/click inputs")
    
except Exception as e:
    print(f"❌ Error: {e}")
