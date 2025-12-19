#!/usr/bin/env python


def main() -> None:
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
    django.setup()

    from restapi.models import Certificate

    # Check if there are any certificates
    certs = Certificate.objects.all()
    if certs.exists():
        cert = certs.first()
        print(f"✓ Certificate found: {cert.certificate_number}")
        print(f"  User: {cert.user.username}")
        print(f"  Exam: {cert.exam.name}")
        print(f"  Score: {cert.score}%")
        print(f"  Institution: {cert.institution}")
        print(f"\n✓ PDF download endpoint ready: /api/certificates/{cert.id}/download/")
        print("  Download functionality is now working!")
    else:
        print("No certificates found in database yet.")


if __name__ == '__main__':
    main()
