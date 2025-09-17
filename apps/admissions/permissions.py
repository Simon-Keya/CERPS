
import logging
from rest_framework import permissions

logger = logging.getLogger(__name__)

ADMISSIONS_GROUPS = {"Admissions", "Registrar", "SuperAdmin"}

class IsAdmissionsStaff(permissions.BasePermission):
    """
    Allows access for users in Admissions, Registrar, or SuperAdmin groups, or superusers.
    """
    def has_permission(self, request, view):
        logger.debug(f"Checking IsAdmissionsStaff for user: {request.user}")
        is_staff = request.user.is_authenticated and (
            request.user.is_superuser or
            request.user.groups.filter(name__in=ADMISSIONS_GROUPS).exists()
        )
        logger.debug(f"IsAdmissionsStaff result: {is_staff}")
        return is_staff

class IsApplicantOrAdmissionsStaff(permissions.BasePermission):
    """
    Allows access for admissions staff or the applicant who owns the object.
    """
    def has_permission(self, request, view):
        logger.debug(f"Checking has_permission for user: {request.user}, method: {request.method}, view: {view}")
        is_authenticated = request.user and request.user.is_authenticated
        logger.debug(f"Is authenticated: {is_authenticated}")
        return is_authenticated

    def has_object_permission(self, request, view, obj):
        logger.debug(f"Checking has_object_permission for user: {request.user}, obj: {obj}")
        if request.user.is_superuser or request.user.groups.filter(name__in=ADMISSIONS_GROUPS).exists():
            logger.debug("User is superuser or in staff groups")
            return True
        owner = getattr(obj, "applicant", None)
        if owner is None and hasattr(obj, "application"):
            owner = getattr(obj.application, "applicant", None)
        is_owner = owner == request.user
        logger.debug(f"Is owner: {is_owner}, owner: {owner}")
        return is_owner
