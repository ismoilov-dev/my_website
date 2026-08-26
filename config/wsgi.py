"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Fallback: ensure static files are collected if staticfiles directory is empty or missing on startup
try:
    from django.conf import settings
    if not os.path.exists(settings.STATIC_ROOT) or not os.listdir(settings.STATIC_ROOT):
        from django.core.management import call_command
        print("Collecting static files on WSGI startup...")
        call_command('collectstatic', interactive=False)
except Exception as e:
    print(f"WSGI static auto-collect fallback note: {e}")
