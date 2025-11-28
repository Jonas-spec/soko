import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_path = Path(__file__).resolve().parent
sys.path.append(str(project_path))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sokohub.settings')

# Try to configure Django
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

# Now we can import settings
from django.conf import settings

print("\n=== Python Environment ===")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

print("\n=== Django Settings ===")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"Settings file: {settings.SETTINGS_MODULE}")

print("\n=== Important Settings ===")
print(f"INSTALLED_APPS: {getattr(settings, 'INSTALLED_APPS', 'Not found')}")
print(f"MIDDLEWARE: {getattr(settings, 'MIDDLEWARE', 'Not found')}")

print("\n=== Paths ===")
print(f"Current directory: {os.getcwd()}")
print(f"Project directory: {project_path}")
print(f"Settings module path: {os.path.join(project_path, 'sokohub', 'settings.py')}")
print(f"Settings module exists: {os.path.exists(os.path.join(project_path, 'sokohub', 'settings.py'))}")