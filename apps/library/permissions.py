from rest_framework.permissions import BasePermission

class IsLibraryStaffOrReadOnly(BasePermission):
    """
    Library staff can manage books and borrow records.
    Other users can only view.
    """
    def has_permission(self, request, view):
        user = request.user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return user and user.is_authenticated
        
        # Write permissions for staff only
        return user and user.is_authenticated and (user.is_staff or user.groups.filter(name='LibraryStaff').exists())

class IsLibraryStaff(BasePermission):
    """
    Allows access only to library staff.
    """
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and (user.is_staff or user.groups.filter(name='LibraryStaff').exists())