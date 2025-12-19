#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import Certificate, Result

# Check all certificates and their scores
certs = Certificate.objects.all()
print(f"Total certificates: {certs.count()}\n")

for cert in certs:
    print(f"Certificate: {cert.certificate_number}")
    print(f"  User: {cert.user.username}")
    print(f"  Exam: {cert.exam.name}")
    print(f"  Score: {cert.score}")
    print(f"  Institution: {cert.institution}")
    
    # Check corresponding result
    result = Result.objects.filter(user=cert.user, exam=cert.exam).first()
    if result:
        print(f"  Result Score: {result.score} (from Result model)")
    print()

# If scores are missing, update them from Result model
print("\n--- Checking for missing scores ---")
for cert in certs:
    if cert.score is None:
        result = Result.objects.filter(user=cert.user, exam=cert.exam).first()
        if result:
            print(f"Updating {cert.certificate_number} with score {result.score}")
            cert.score = result.score
            cert.save()
            print(f"  ✓ Updated!")
        else:
            print(f"No result found for {cert.certificate_number}")
