# cerps/__init__.py

# This ensures that the Celery app is loaded when Django starts
from .config.celery_app import app as celery_app

# Optionally, you can expose the Celery app as a top-level variable
__all__ = ("celery_app",)
