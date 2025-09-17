from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff

class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        has_instructor_profile = hasattr(request.user, 'instructor_profile')
        is_staff = request.user.is_staff
        logger.debug(f"User: {request.user}, Action: {view.action}, Authenticated: {request.user.is_authenticated}, "
                     f"IsStaff: {is_staff}, HasInstructorProfile: {has_instructor_profile}")
        return (
            request.user.is_authenticated and
            (is_staff or has_instructor_profile)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        has_instructor_profile = hasattr(request.user, 'instructor_profile')
        is_staff = request.user.is_staff
        logger.debug(f"Object: {obj}, User: {request.user}, Action: {view.action}, "
                     f"IsStaff: {is_staff}, HasInstructorProfile: {has_instructor_profile}")
        return (
            request.user.is_authenticated and
            (is_staff or has_instructor_profile)
        )