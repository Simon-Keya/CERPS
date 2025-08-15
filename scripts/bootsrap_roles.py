import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cerps.settings")
django.setup()

from django.contrib.auth.models import Group, Permission
from apps.users.models import CustomUser

# Define groups and their permissions
GROUPS_PERMISSIONS = {
    "Admin": ["add_user", "change_user", "delete_user", "view_user"],
    "Faculty": ["view_student", "change_student", "view_course"],
    "HR": ["view_employee", "change_employee"],
    "Finance": ["view_fee", "change_fee"],
    "Student": ["view_own_profile", "view_own_fee"],
}

def create_groups():
    for group_name, perms in GROUPS_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=group_name)
        for perm_codename in perms:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"Permission {perm_codename} not found")

    print("Groups and permissions created successfully.")

if __name__ == "__main__":
    create_groups()
