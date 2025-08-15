from rest_framework.permissions import BasePermission

class IsLibraryStaffOrReadOnly(BasePermission):
    """
    Library staff can manage books and borrow records.
    Students and other roles can only view.
    """
    def has_permission(self, request, view):
        user = request.user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return user.is_authenticated
        return user.is_staff or getattr(user, 'is_library_staff', False)
