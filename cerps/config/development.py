"""
Local development settings for cerps project.
"""

from .base import *

# Override settings for local development
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB", ""),
        'USER': os.environ.get("POSTGRES_USER", ""),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD", ""),
        'HOST': os.environ.get("POSTGRES_HOST", ""),
        'PORT': os.environ.get("POSTGRES_PORT", 5432),
    }
}