from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('login_id', 'first_name', 'last_name', 'is_staff', 'is_student', 'is_faculty', 'is_finance', 'is_hr')
    list_filter = ('is_staff', 'is_student', 'is_faculty', 'is_finance', 'is_hr')
    search_fields = ('login_id', 'first_name', 'last_name')
    ordering = ('login_id',)
    fieldsets = (
        (None, {'fields': ('login_id', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Roles', {'fields': ('is_student', 'is_faculty', 'is_finance', 'is_hr')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login_id', 'password1', 'password2', 'is_student', 'is_staff'),
        }),
    )
