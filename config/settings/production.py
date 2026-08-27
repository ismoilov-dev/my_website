import os

from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

# A real secret must come from the environment. Failing here at boot is far
# better than silently serving production with the development fallback key.
SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY or SECRET_KEY.startswith('django-insecure'):
    raise ImproperlyConfigured(
        'SECRET_KEY must be set to a real secret in production. Generate one with: '
        'python -c "from django.core.management.utils import get_random_secret_key; '
        'print(get_random_secret_key())"'
    )

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS must be set in production.')

# Production Security Hardening
# nginx terminates TLS, so Django learns the original scheme from this header.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() in ['true', '1', 'yes', 'on']
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ['true', '1', 'yes', 'on']
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() in ['true', '1', 'yes', 'on']

SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ['true', '1', 'yes', 'on']
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'True').lower() in ['true', '1', 'yes', 'on']

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True

# Production Storage
# The manifest backend fingerprints every file (main.css -> main.a1b2c3.css), so
# a redeploy invalidates browser caches instead of serving last month's CSS.
STORAGES = {
    'default': {
        'BACKEND': os.environ.get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage'),
    },
    'staticfiles': {
        'BACKEND': os.environ.get(
            'STATICFILES_STORAGE',
            'whitenoise.storage.CompressedManifestStaticFilesStorage',
        ),
    },
}

# Fingerprinted files never change, so they can be cached indefinitely.
WHITENOISE_MAX_AGE = 31536000
