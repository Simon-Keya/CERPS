from rest_framework.permissions import BasePermission

class IsFinanceAdmin(BasePermission):
    """Allow only staff to access finance endpoints"""
    def has_permission(self, request, view):
        return request.user.is_staff
