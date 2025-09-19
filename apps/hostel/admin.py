from django.contrib import admin
from .models import Hostel, Floor, Room, Bed, Student, Booking, Complaint

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'capacity', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'address']
    ordering = ['name']
    date_hierarchy = 'created_at'

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'number', 'description']
    list_filter = ['hostel']
    search_fields = ['hostel__name', 'description']
    ordering = ['hostel__name', 'number']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['floor', 'number', 'room_type', 'capacity', 'is_available']
    list_filter = ['room_type', 'is_available', 'floor__hostel']
    search_fields = ['number', 'floor__hostel__name']
    ordering = ['floor__hostel__name', 'number']

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['room', 'number', 'is_occupied']
    list_filter = ['is_occupied', 'room__floor__hostel']
    search_fields = ['number', 'room__number', 'room__floor__hostel__name']
    ordering = ['room__floor__hostel__name', 'room__number', 'number']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'registration_number', 'phone_number', 'created_at']
    list_filter = []
    search_fields = ['registration_number', 'user__username', 'user__email', 'phone_number']
    ordering = ['registration_number']
    date_hierarchy = 'created_at'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['student', 'bed', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'start_date', 'bed__room__floor__hostel']
    search_fields = ['student__registration_number', 'student__user__username', 'bed__number', 'bed__room__number']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['student', 'title', 'status', 'created_at', 'resolved_at']
    list_filter = ['status', 'created_at', 'resolved_at']
    search_fields = ['title', 'description', 'student__registration_number', 'student__user__username']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
