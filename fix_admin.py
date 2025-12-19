#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_admin_user():
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.set_password('user123')
        admin_user.role = 'admin'
        admin_user.save()
        print(f'Admin user fixed: {admin_user.username}')
        print(f'  - Password set to: user123')
        print(f'  - Role: {admin_user.role}')
        print(f'  - Is staff: {admin_user.is_staff}')
        print(f'  - Certificate ID: {admin_user.certificate_id}')
    except User.DoesNotExist:
        print('Admin user not found, creating...')
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='user123'
        )
        admin_user.role = 'admin'
        admin_user.save()
        print(f'Admin user created: {admin_user.username}')

    # List all users
    print('\nAll users:')
    for user in User.objects.all():
        print(f'  {user.username}: staff={user.is_staff}, role={user.role}, cert_id={user.certificate_id}')

if __name__ == "__main__":
    fix_admin_user()