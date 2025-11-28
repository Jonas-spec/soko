import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent 
print(f"Correct BASE_DIR: {BASE_DIR}")

# Templates
TEMPLATES = [
    {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'sokohub', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==========================================
# CRITICAL FIX FOR LOGIN/LOGOUT ERRORS
# ==========================================
# We use 'accounts:login' because you defined app_name='accounts' in your urls.py
LOGIN_URL = 'accounts:login'
LOGOUT_REDIRECT_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home'  # Redirects here after successful login
# In your settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Print the template directories being searched (Debug info)
import django.template.utils
try:
    print("\nTemplate directories:")
    for template_dir in django.template.utils.get_app_template_dirs('templates'):
        print(f"- {template_dir}")
    print(f"- {os.path.join(BASE_DIR, 'templates')}\n")
except Exception:
    pass