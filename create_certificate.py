#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Result, Certificate, CustomUser
import uuid

user = CustomUser.objects.get(username='user1')
result = Result.objects.get(user=user)

print(f"User: {result.user.username}")
print(f"Exam: {result.exam.name}")
print(f"Score: {result.score}%")
print(f"Passed: {result.passed}\n")

if result.passed:
    # Check if certificate already exists
    if Certificate.objects.filter(user=result.user, exam=result.exam).exists():
        print("⚠️  Certificate already exists for this exam")
        cert = Certificate.objects.get(user=result.user, exam=result.exam)
        print(f"   Certificate ID: {cert.certificate_number}")
    else:
        # Create certificate
        cert_number = f"CERT-{uuid.uuid4().hex[:10].upper()}"
        
        certificate = Certificate.objects.create(
            user=result.user,
            exam=result.exam,
            certificate_number=cert_number,
            name=result.user.get_full_name() or result.user.username,
            institution="Demo University",
            score=result.score
        )
        
        print(f"✅ Certificate created successfully!")
        print(f"   Certificate Number: {certificate.certificate_number}")
        print(f"   Name: {certificate.name}")
        print(f"   Exam: {certificate.exam.name}")
        print(f"   Institution: {certificate.institution}")
        print(f"   Score: {certificate.score}%")
        print(f"   Issued: {certificate.issued_date}")
else:
    print("❌ Cannot create certificate - exam not passed")
