from django.contrib import admin
from .models import Department, Employee, LeaveRequest

# Check if already registered to avoid duplicates
if not admin.site.is_registered(Department):
    @admin.register(Department)
    class DepartmentAdmin(admin.ModelAdmin):
        list_display = ['name', 'description', 'created_at']
        search_fields = ['name']

if not admin.site.is_registered(Employee):
    @admin.register(Employee)
    class EmployeeAdmin(admin.ModelAdmin):
        list_display = ['employee_id', 'user', 'position', 'department', 'hire_date']
        search_fields = ['employee_id', 'user__login_id']
        list_filter = ['department']

if not admin.site.is_registered(LeaveRequest):
    @admin.register(LeaveRequest)
    class LeaveRequestAdmin(admin.ModelAdmin):
        list_display = ['employee', 'start_date', 'end_date', 'status']
        list_filter = ['status']
        search_fields = ['employee__user__login_id']