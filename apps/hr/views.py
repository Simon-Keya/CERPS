from rest_framework import viewsets
from apps.hr.models import Department, Employee, LeaveRequest
from apps.hr.serializers import DepartmentSerializer, EmployeeSerializer, LeaveRequestSerializer
from apps.hr.permissions import IsHRStaffOrReadOnly, IsHREmployeeOrHRStaff
import logging

logger = logging.getLogger(__name__)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsHRStaffOrReadOnly]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsHRStaffOrReadOnly]

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsHREmployeeOrHRStaff]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        logger.debug(f"User: {user}, Action: {self.action}, Authenticated: {user.is_authenticated}")
        if self.action in ['list']:
            if user.is_authenticated and (user.is_staff or user.is_hr or user.groups.filter(name__in=['HR', 'SuperAdmin']).exists()):
                logger.debug("Returning all leave requests for HR user")
                return LeaveRequest.objects.all()
            logger.debug(f"Returning leave requests for user: {user}")
            return LeaveRequest.objects.filter(employee__user=user)
        logger.debug("Returning all leave requests for object-level actions")
        return LeaveRequest.objects.all()