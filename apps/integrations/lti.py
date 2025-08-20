"""
Minimal LTI-like helpers and a Moodle REST sync example.
For proper LTI Tool Provider / Consumer, use pylti or ims_lti libraries.
This file offers:
 - simple course/enrollment sync via Moodle REST API
 - placeholder LTI launch endpoint handler
"""

import requests
from django.conf import settings
from apps.academic.models import Course, Section
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Moodle REST API sync example
def fetch_moodle_courses(moodle_base_url: str, token: str):
    """
    Calls Moodle's core_course_get_courses or other endpoints.
    Returns list of course dicts.
    """
    url = f"{moodle_base_url}/webservice/rest/server.php"
    params = {"wstoken": token, "wsfunction": "core_course_get_courses", "moodlewsrestformat": "json"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def sync_moodle_courses(moodle_base_url: str, token: str):
    courses = fetch_moodle_courses(moodle_base_url, token)
    created = 0
    updated = 0
    for c in courses:
        code = str(c.get("shortname") or c.get("idnumber") or c.get("id"))
        title = c.get("fullname") or c.get("name")
        # upsert Course
        course_obj, created_flag = Course.objects.update_or_create(code=code, defaults={"title": title})
        if created_flag:
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated, "total": len(courses)}

# Minimal placeholder for LTI launch validation -- **not production LTI**
def validate_lti_launch(request):
    # For production implement oauth1 signature validation per LTI spec.
    consumer_key = settings.LTI_CONSUMER_KEY
    consumer_secret = settings.LTI_CONSUMER_SECRET
    # Implement oauth signature check (omitted for brevity)
    return True
