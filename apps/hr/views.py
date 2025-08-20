from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.utils import log_action
from .models import Department, Employee, LeaveRequest
from .serializers import DepartmentSerializer, EmployeeSerializer, LeaveRequestSerializer
from .permissions import IsHRStaffOrReadOnly, IsHREmployeeOrHRStaff

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsHRStaffOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'created_department', {'department_id': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'updated_department', {'department_id': instance.id})

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department']
    search_fields = ['user__login_id', 'employee_id', 'position']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'created_employee', {'employee_id': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'updated_employee', {'employee_id': instance.id})

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee__user').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsHREmployeeOrHRStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'employee']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name__in=['HR', 'SuperAdmin']).exists():
            return self.queryset
        return self.queryset.filter(employee__user=user)

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'created_leave_request', {'leave_request_id': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'updated_leave_request', {'leave_request_id': instance.id})