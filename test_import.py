import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'test-key-for-debugging-123'
DEBUG = True
ALLOWED_HOSTS = []

# Rest of your settings...