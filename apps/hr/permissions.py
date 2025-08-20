from rest_framework import permissions

class IsHRStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or
            request.user.groups.filter(name__in=['HR', 'SuperAdmin']).exists()
        )

class IsHREmployeeOrHRStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.groups.filter(name__in=['HR', 'SuperAdmin']).exists() or hasattr(request.user, 'employee_profile')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # HR staff or superusers can edit all leave requests; employees can edit their own
        return (
            request.user.is_staff or
            request.user.groups.filter(name__in=['HR', 'SuperAdmin']).exists() or
            (hasattr(request.user, 'employee_profile') and obj.employee == request.user.employee_profile)
        )