import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project: BASE_DIR is project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-dev-key-change-in-env')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes', 'on']

# ALLOWED_HOSTS configuration
env_allowed_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in env_allowed_hosts.split(',') if h.strip()]

# Render host automatically appended if provided
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF TRUSTED ORIGINS
env_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env_csrf_origins.split(',') if o.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'blog',
    'analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'analytics.middleware.TrackVisitorMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.site_identity',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration with dj-database-url
# Default fallback to local SQLite if DATABASE_URL is not set
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Option to build from individual POSTGRES_* environment variables if present
    pg_db = os.environ.get('POSTGRES_DB')
    pg_user = os.environ.get('POSTGRES_USER')
    pg_password = os.environ.get('POSTGRES_PASSWORD')
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')

    if pg_db and pg_user:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': pg_db,
                'USER': pg_user,
                'PASSWORD': pg_password,
                'HOST': pg_host,
                'PORT': pg_port,
                'CONN_MAX_AGE': 600,
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Tashkent')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'blog' / 'static',
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise storage default setup
STORAGES = {
    'default': {
        'BACKEND': os.environ.get('DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage'),
    },
    'staticfiles': {
        'BACKEND': os.environ.get('STATICFILES_STORAGE', 'whitenoise.storage.CompressedStaticFilesStorage'),
    },
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'blog': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# Public identity
# ---------------
# The footer links and the schema.org "sameAs" block must list exactly the same
# profiles: search engines use sameAs to tie this site to the same person as
# those accounts, and a mismatch weakens that signal. Defining them once here
# means the two can never drift apart.
SITE_AUTHOR = 'Ismat Ismoilov'

# Uzbek usage puts the family name first, so people search both orders.
SITE_AUTHOR_ALTERNATES = ['Ismoilov Ismat', 'Ismat Ismoilov']

SITE_JOB_TITLE = 'Python Backend Developer'

SOCIAL_PROFILES = [
    ('GitHub', 'https://github.com/ismoilov-dev'),
    ('LinkedIn', 'https://linkedin.com/in/ismoilov-ismat'),
    ('Telegram', 'https://t.me/lazy_devvbek'),
    ('YouTube', 'https://youtube.com/@ismoilov-dev'),
]

# Filled in from the environment with the token Google Search Console hands out
# when verifying ownership by meta tag. Empty means no tag is rendered.
GOOGLE_SITE_VERIFICATION = os.environ.get('GOOGLE_SITE_VERIFICATION', '')

# The other Search Console method: Google fetches a file whose name it chose,
# and the body simply names the file back. Set this to that exact filename,
# e.g. googleabc123.html. Leaving it empty removes the route entirely, which
# matters -- answering any google*.html request would let a stranger verify
# ownership of this site in their own Search Console account.
GOOGLE_SITE_VERIFICATION_FILE = os.environ.get('GOOGLE_SITE_VERIFICATION_FILE', '')
