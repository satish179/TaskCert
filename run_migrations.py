#!/usr/bin/env python
"""
Run Django migrations on Vercel/Neon database.
This script should be run once after deploying to set up the database tables.
"""
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

import django
django.setup()

from django.core.management import call_command

print("Running migrations...")
call_command('migrate', '--noinput')

print("\nCreating superuser (if not exists)...")
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin'
    )
    print("✅ Superuser created: username=admin, password=admin123")
else:
    print("ℹ️  Superuser already exists")

print("\n✅ Database setup complete!")
