#!/usr/bin/env python
"""
Script to populate sample questions and topics for the Task Certification Platform
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Topic, SampleQuestion

def create_sample_data():
    """Create sample topics and questions"""

    # Create topics
    topics_data = [
        {
            'name': 'Python Programming',
            'description': 'Fundamental concepts and advanced topics in Python programming',
        },
        {
            'name': 'Django Framework',
            'description': 'Web development with Django framework',
        },
        {
            'name': 'Database Management',
            'description': 'SQL, database design, and data management concepts',
        },
        {
            'name': 'Web Development',
            'description': 'HTML, CSS, JavaScript, and modern web technologies',
        },
        {
            'name': 'Data Structures & Algorithms',
            'description': 'Essential data structures and algorithmic problem solving',
        },
    ]

    topics = {}
    for topic_data in topics_data:
        topic, created = Topic.objects.get_or_create(
            name=topic_data['name'],
            defaults={
                'description': topic_data['description'],
                'is_active': True
            }
        )
        topics[topic_data['name']] = topic
        if created:
            print(f"Created topic: {topic.name}")
        else:
            print(f"Topic already exists: {topic.name}")

    # Create sample questions
    questions_data = [
        # Python Programming
        {
            'topic': 'Python Programming',
            'question_text': 'What is the output of: print(2 ** 3 ** 2)',
            'question_type': 'multiple_choice',
            'options': ['64', '512', '8', '16'],
            'correct_answer': '512',
            'explanation': 'Exponentiation is right-associative, so 3 ** 2 is evaluated first (9), then 2 ** 9 = 512.',
            'difficulty_level': 'intermediate'
        },
        {
            'topic': 'Python Programming',
            'question_text': 'Which of the following is NOT a valid Python data type?',
            'question_type': 'multiple_choice',
            'options': ['int', 'str', 'float', 'double'],
            'correct_answer': 'double',
            'explanation': 'Python does not have a "double" data type. It uses "float" for floating-point numbers.',
            'difficulty_level': 'beginner'
        },
        {
            'topic': 'Python Programming',
            'question_text': 'What does the "self" parameter represent in a Python class method?',
            'question_type': 'short_answer',
            'correct_answer': 'A reference to the current instance of the class',
            'explanation': '"self" is a convention in Python that refers to the instance of the class. It allows access to instance variables and methods.',
            'difficulty_level': 'beginner'
        },

        # Django Framework
        {
            'topic': 'Django Framework',
            'question_text': 'Which command is used to create a new Django project?',
            'question_type': 'multiple_choice',
            'options': ['django-admin startproject', 'python manage.py startproject', 'django create-project', 'python -m django startproject'],
            'correct_answer': 'django-admin startproject',
            'explanation': 'The django-admin startproject command creates a new Django project with the basic directory structure.',
            'difficulty_level': 'beginner'
        },
        {
            'topic': 'Django Framework',
            'question_text': 'What is the purpose of Django\'s ORM (Object-Relational Mapping)?',
            'question_type': 'short_answer',
            'correct_answer': 'To provide a high-level abstraction for database operations',
            'explanation': 'Django ORM allows developers to interact with databases using Python objects instead of writing raw SQL queries.',
            'difficulty_level': 'intermediate'
        },

        # Database Management
        {
            'topic': 'Database Management',
            'question_text': 'What does ACID stand for in database transactions?',
            'question_type': 'multiple_choice',
            'options': ['Atomicity, Consistency, Isolation, Durability', 'Access, Control, Integrity, Data', 'Automatic, Consistent, Independent, Durable', 'All, Complete, Isolated, Done'],
            'correct_answer': 'Atomicity, Consistency, Isolation, Durability',
            'explanation': 'ACID properties ensure reliable database transactions: Atomicity (all-or-nothing), Consistency (valid state), Isolation (concurrent transactions), Durability (permanent changes).',
            'difficulty_level': 'intermediate'
        },
        {
            'topic': 'Database Management',
            'question_text': 'Which SQL clause is used to filter records?',
            'question_type': 'multiple_choice',
            'options': ['SELECT', 'WHERE', 'FROM', 'ORDER BY'],
            'correct_answer': 'WHERE',
            'explanation': 'The WHERE clause is used to filter records based on specified conditions.',
            'difficulty_level': 'beginner'
        },

        # Web Development
        {
            'topic': 'Web Development',
            'question_text': 'What does CSS stand for?',
            'question_type': 'multiple_choice',
            'options': ['Computer Style Sheets', 'Cascading Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'],
            'correct_answer': 'Cascading Style Sheets',
            'explanation': 'CSS stands for Cascading Style Sheets, used for describing the presentation of web documents.',
            'difficulty_level': 'beginner'
        },
        {
            'topic': 'Web Development',
            'question_text': 'Which HTML tag is used to create a hyperlink?',
            'question_type': 'multiple_choice',
            'options': ['<link>', '<a>', '<href>', '<url>'],
            'correct_answer': '<a>',
            'explanation': 'The <a> tag (anchor tag) is used to create hyperlinks in HTML.',
            'difficulty_level': 'beginner'
        },

        # Data Structures & Algorithms
        {
            'topic': 'Data Structures & Algorithms',
            'question_text': 'What is the time complexity of binary search?',
            'question_type': 'multiple_choice',
            'options': ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
            'correct_answer': 'O(log n)',
            'explanation': 'Binary search has O(log n) time complexity because it repeatedly divides the search space in half.',
            'difficulty_level': 'intermediate'
        },
        {
            'topic': 'Data Structures & Algorithms',
            'question_text': 'Which data structure follows Last In First Out (LIFO) principle?',
            'question_type': 'multiple_choice',
            'options': ['Queue', 'Stack', 'Array', 'Linked List'],
            'correct_answer': 'Stack',
            'explanation': 'A stack follows the LIFO principle - the last element added is the first one to be removed.',
            'difficulty_level': 'beginner'
        },
    ]

    for question_data in questions_data:
        topic = topics[question_data['topic']]
        question, created = SampleQuestion.objects.get_or_create(
            topic=topic,
            question_text=question_data['question_text'],
            defaults={
                'question_type': question_data['question_type'],
                'options': question_data.get('options'),
                'correct_answer': question_data['correct_answer'],
                'explanation': question_data['explanation'],
                'difficulty_level': question_data['difficulty_level'],
                'is_active': True
            }
        )
        if created:
            print(f"Created question: {question.question_text[:50]}...")
        else:
            print(f"Question already exists: {question.question_text[:50]}...")

    print("\nSample data creation completed!")
    print(f"Topics created: {Topic.objects.count()}")
    print(f"Questions created: {SampleQuestion.objects.count()}")

if __name__ == '__main__':
    create_sample_data()