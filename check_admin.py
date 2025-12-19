#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from restapi.models import CustomUser

# Check for admin users
admins = CustomUser.objects.filter(is_staff=True)
print(f"\nTotal staff/admin users: {admins.count()}")

for user in admins:
    print(f"  - Username: {user.username}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")

# Check if admin user exists
admin = CustomUser.objects.filter(username='admin').first()

if admin:
    print(f"\nAdmin user 'admin' found!")
    print(f"  Email: {admin.email}")
    print(f"  Is Staff: {admin.is_staff}")
    print(f"  Is Superuser: {admin.is_superuser}")
    print(f"  Password hash: {admin.password[:40]}...")
else:
    print("\nAdmin user 'admin' NOT found. Creating...")
    admin = CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print(f"✓ Admin user created successfully!")
    print(f"  Username: admin")
    print(f"  Password: admin123")
    print(f"  Email: admin@example.com")

# Also check for user1
print(f"\n\nAll users in database:")
for user in CustomUser.objects.all():
    print(f"  - {user.username} (staff={user.is_staff})")
