# cerps/config/celery_app.py

import os
from celery import Celery

# Make sure this path is correct
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cerps.config.development")

app = Celery("cerps")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
