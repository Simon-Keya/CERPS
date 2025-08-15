import requests
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cerps.settings")
django.setup()

from apps.users.models import CustomUser

MOODLE_API_URL = "https://yourmoodle.com/webservice/rest/server.php"
MOODLE_TOKEN = "your_token_here"

def sync_students():
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_user_get_users",
        "criteria[0][key]": "username",
        "criteria[0][value]": "%",
        "moodlewsrestformat": "json"
    }
    response = requests.get(MOODLE_API_URL, params=params)
    data = response.json()
    for student in data.get("users", []):
        if not CustomUser.objects.filter(username=student["username"]).exists():
            CustomUser.objects.create_user(
                username=student["username"],
                first_name=student["firstname"],
                last_name=student["lastname"],
                email=student["email"],
                password="defaultpass",
                is_student=True
            )
            print(f"Synced student: {student['username']}")

if __name__ == "__main__":
    sync_students()
