import os
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cerps.settings")
django.setup()

from apps.reporting.models import KPI

def generate_daily_reports():
    kpis = KPI.objects.all()
    for kpi in kpis:
        print(f"[{datetime.now()}] KPI: {kpi.name} - Value: {kpi.value}")

if __name__ == "__main__":
    generate_daily_reports()
