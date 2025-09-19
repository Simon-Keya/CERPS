from rest_framework import permissions

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff members to edit objects.
    Read-only access is allowed for any authenticated user.
    """

    def has_permission(self, request, view):
        # Allow read-only permissions for any safe HTTP methods.
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions are only allowed to staff users.
        return request.user and request.user.is_staff

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff members to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner or staff.
        return obj.user == request.user or request.user.is_staff

class IsStaff(permissions.BasePermission):
    """
    Custom permission to only allow staff members access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow superusers access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser