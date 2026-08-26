import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT', os.environ.get('DJANGO_ENV', 'local')).lower()

if ENVIRONMENT in ['production', 'prod'] or os.environ.get('DEBUG', 'True').lower() in ['false', '0', 'no', 'off']:
    from .production import *
else:
    from .local import *
