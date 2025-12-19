import os
import django
from django.test import RequestFactory
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.views import ResultViewSet
from restapi.models import Exam, Question, Mentor, CustomUser, Task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def verify():
    print("Setting up test data...")
    # Create required data
    try:
        mentor = Mentor.objects.first()
        if not mentor:
            user = User.objects.create_user(username='mentor_test', password='password', is_staff=True)
            mentor = Mentor.objects.create(user=user, name='Test Mentor', email='test@test.com')

        student = User.objects.filter(username='student_test_verify').first()
        if not student:
            student = User.objects.create_user(username='student_test_verify', password='password')

        # Clean old tests
        Exam.objects.filter(name='Verify Fix Exam').delete()

        exam = Exam.objects.create(
            name='Verify Fix Exam',
            created_by=mentor,
            duration_minutes=60,
            pass_score=50
        )
        
        # Ensure student has access (tasks completed)
        # For simplicity, we can just assign the exam to the student directly if the view supports it,
        # but the view checks for "completed all tasks".
        # Or we can create a dummy task and complete it.
        task = Task.objects.create(
            name='Dummy Task',
            assigned_by=mentor,
            assigned_to=student,
            due_date=timezone.now(),
            status='completed'
        )

        # Create a True/False question with NO options
        q1 = Question.objects.create(
            exam=exam,
            question_text='Is this a test?',
            question_type='true_false',
            options=None, # Explicitly None
            correct_answer='True'
        )
        print(f"Created Question: {q1.question_text} (Type: {q1.question_type}, Options in DB: {q1.options})")

        # Simulate Request
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        data = {'exam_id': exam.id}
        request = factory.post('/api/results/start_exam/', 
                             data, 
                             format='json')
        request.data = data # Manually attach data since we are bypassing DRF's dispatch
        request.user = student
        
        view = ResultViewSet()
        view.action_map = {'post': 'start_exam'}
        view.request = request
        view.format_kwarg = None

        print("Calling start_exam...")
        response = view.start_exam(request)
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            questions = data.get('questions', [])
            for q in questions:
                if q['id'] == q1.id:
                    print(f"Returned Question Options: {q['options']}")
                    if q['options'] and 'True' in q['options'] and 'False' in q['options']:
                        print("SUCCESS: Default options were injected!")
                    else:
                        print("FAILURE: Options are still missing or incorrect.")
        else:
            print(f"Error: {response.data}")

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if 'exam' in locals():
            exam.delete()
        if 'student' in locals() and student:
            # Maybe keep student if re-running, but deleting is cleaner if unique username
             student.delete()
        print("Test finished.")

if __name__ == '__main__':
    verify()
