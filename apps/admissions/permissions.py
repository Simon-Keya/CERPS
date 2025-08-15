from rest_framework import permissions

ADMISSIONS_GROUPS = {"Admissions", "Registrar", "SuperAdmin"}  # you can adjust group names

def user_in_groups(user, group_names):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=group_names).exists())


class IsAdmissionsStaff(permissions.BasePermission):
    """
    Staff-only create/update/delete; read allowed to admissions staff;
    applicants can see their own applications.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # allow authenticated users to read; object-level filter will apply
            return bool(request.user and request.user.is_authenticated)
        # non-safe methods require admissions staff
        return user_in_groups(request.user, ADMISSIONS_GROUPS)

    def has_object_permission(self, request, view, obj):
        # Admissions staff can do everything
        if user_in_groups(request.user, ADMISSIONS_GROUPS):
            return True
        # Applicants can only read their own objects
        if request.method in permissions.SAFE_METHODS:
            owner = getattr(obj, "applicant", None)
            # for nested objects like documents/reviews, derive owner
            if owner is None and hasattr(obj, "application"):
                owner = getattr(obj.application, "applicant", None)
            return owner == request.user
        return False
