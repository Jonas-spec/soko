import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = 'django-insecure-$(gy*zdk8q3_fml8*2yqg4v4^#1b^p9r3yrhh5iqs3$z_jg3m#'
DEBUG = False
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vendor.apps.VendorConfig',
    'accounts',
    'products',
    'orders',
    'vendors',  # Add this line
    'crispy_forms',
    'crispy_bootstrap5',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # This must be before AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # This requires SessionMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',     # This requires SessionMiddleware
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.RoleBasedAuthMiddleware',  # Your custom middleware
]

ROOT_URLCONF = 'sokohub.urls'

TEMPLATES = [
    {'BACKEND': 'django.template.backends.django.DjangoTemplates',
         'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'sokohub.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
# or whatever your custom user model is called
# Authentication
LOGIN_URL = 'accounts:login'  # Updated to use namespace
LOGIN_REDIRECT_URL = 'home'   # Add this line to specify where to redirect after login
LOGOUT_REDIRECT_URL = 'home'  # Updated to use namespace
LOGOUT_URL = 'accounts:logout'  # Add this line

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
# settings.py

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'izabayojonas457@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'rvps cwnp hvje next'  # Replace with your App Password
DEFAULT_FROM_EMAIL = 'izabayojonas457@gmail.com'  # Should match EMAIL_HOST_USER