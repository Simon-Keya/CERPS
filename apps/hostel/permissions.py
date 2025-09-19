from rest_framework import permissions

class IsHostelAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or
            request.user.groups.filter(name__in=['HostelAdmin', 'SuperAdmin']).exists()
        )

class IsStudentOrHostelAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            hasattr(obj, 'student') and obj.student.user == request.user or
            request.user.is_superuser or
            request.user.groups.filter(name__in=['HostelAdmin', 'SuperAdmin']).exists()
        )
