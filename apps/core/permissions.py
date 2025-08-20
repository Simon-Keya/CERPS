from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    """
    Allows read access to everyone, but write access only to admin users.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff

class AuditLogPermission(BasePermission):
    """
    Custom permission for audit logs: read-only for authenticated users, full access for admins.
    """
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.is_authenticated
        return request.user.is_staff