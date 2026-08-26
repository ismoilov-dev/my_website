import os
from .base import *

DEBUG = False

# Production Security Hardening
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() in ['true', '1', 'yes', 'on']
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ['true', '1', 'yes', 'on']
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() in ['true', '1', 'yes', 'on']

SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ['true', '1', 'yes', 'on']
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'True').lower() in ['true', '1', 'yes', 'on']

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Production Storage
STORAGES = {
    'default': {
        'BACKEND': os.environ.get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage'),
    },
    'staticfiles': {
        'BACKEND': os.environ.get('STATICFILES_STORAGE', 'whitenoise.storage.CompressedStaticFilesStorage'),
    },
}
