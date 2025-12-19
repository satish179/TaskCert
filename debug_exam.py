import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Exam

def inspect():
    exam = Exam.objects.filter(name__icontains='Django').first()
    if not exam:
        print("No Django exam found")
        return

    questions = []
    for q in exam.questions.all():
        questions.append({
            'text': q.question_text,
            'type': q.question_type,
            'options': q.options
        })
    
    print(json.dumps(questions, indent=2))

if __name__ == '__main__':
    inspect()
