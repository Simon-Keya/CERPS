from rest_framework.permissions import BasePermission

class IsHostelStaffOrReadOnly(BasePermission):
    """
    Only staff can manage hostel data, students can view their own info.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        return request.user.is_staff or getattr(request.user, 'is_hostel_staff', False)
