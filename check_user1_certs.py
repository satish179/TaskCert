#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Certificate, CustomUser

# Get user1 (the test user)
try:
    user1 = CustomUser.objects.get(username='user1')
    certs = Certificate.objects.filter(user=user1).select_related('exam')
    
    print(f"Certificates for user1: {certs.count()}")
    for cert in certs:
        print(f"\nCertificate ID: {cert.id}")
        print(f"  Certificate Number: {cert.certificate_number}")
        print(f"  Exam: {cert.exam.name}")
        print(f"  Score: {cert.score}")
        print(f"  Score Type: {type(cert.score)}")
        print(f"  Score is None: {cert.score is None}")
        print(f"  Institution: {cert.institution}")
        print(f"  Name: {cert.name}")
except CustomUser.DoesNotExist:
    print("user1 not found")
