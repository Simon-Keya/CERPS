from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, EmployeeViewSet, LeaveRequestViewSet

app_name = 'hr'

router = DefaultRouter()
router.register(r'api/departments', DepartmentViewSet, basename='department')
router.register(r'api/employees', EmployeeViewSet, basename='employee')
router.register(r'api/leaverequests', LeaveRequestViewSet, basename='leaverequest')

urlpatterns = [
    path('', include(router.urls)),
]