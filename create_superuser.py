import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@hospital.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    print(f"Creating default superuser '{username}'...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully.")
else:
    print(f"Superuser '{username}' already exists.")

# Automatically seed sample data if no doctors exist yet
try:
    from hospital.models import Doctor
    if Doctor.objects.count() == 0:
        print("No doctors found. Running seed_data...")
        call_command('seed_data')
        print("Sample data populated successfully.")
except Exception as e:
    print("Notice during initial data check:", e)
