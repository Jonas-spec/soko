# SOKOHUB Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- Stripe account
- Domain name (optional)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd SOKOHUB
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Stripe Setup

1. **Create a Stripe account** at https://stripe.com
2. **Get your API keys** from the Stripe Dashboard
3. **Add keys to .env file**:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```
4. **For production**, use live keys (pk_live_... and sk_live_...)

## Deployment Options

### Option 1: Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_...
   heroku config:set STRIPE_SECRET_KEY=sk_live_...
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```

6. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Option 2: Railway

1. **Connect your GitHub repository** to Railway
2. **Add environment variables** in Railway dashboard
3. **Railway will automatically detect** and deploy your Django app
4. **Add PostgreSQL** service in Railway
5. **Run migrations** via Railway CLI or dashboard

### Option 3: DigitalOcean App Platform

1. **Create a new app** in DigitalOcean
2. **Connect your GitHub repository**
3. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Run Command: `gunicorn sokohub.wsgi`
4. **Add environment variables**
5. **Add PostgreSQL database**
6. **Deploy**

### Option 4: AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   eb init -p python-3.11 sokohub
   ```

3. **Create environment**
   ```bash
   eb create sokohub-env
   ```

4. **Set environment variables**
   ```bash
   eb setenv SECRET_KEY=... STRIPE_PUBLISHABLE_KEY=...
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

## Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure static files (WhiteNoise or S3)
- [ ] Set up media files storage (S3 recommended)
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS
- [ ] Configure security headers
- [ ] Set up error logging
- [ ] Use Stripe live keys
- [ ] Set up backup strategy
- [ ] Configure domain name
- [ ] Set up monitoring

## Security Settings for Production

Update `sokohub/local_settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Static Files (Production)

For production, use WhiteNoise (already in requirements.txt):

```python
MIDDLEWARE = [
    # ...
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Media Files (Production)

For production, use AWS S3 or similar:

1. Install `django-storages` and `boto3`
2. Configure in settings:
```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
```

## Troubleshooting

- **Static files not loading**: Run `python manage.py collectstatic`
- **Database errors**: Check database connection and run migrations
- **Stripe errors**: Verify API keys are correct
- **500 errors**: Check logs and ensure DEBUG=False in production

## Support

For issues, check:
- Django documentation: https://docs.djangoproject.com/
- Stripe documentation: https://stripe.com/docs
- Deployment platform documentation

