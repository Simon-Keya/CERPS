from django.contrib import admin
from .models import Hostel, Room, HostelMember

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_rooms')
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'room_number', 'capacity', 'occupants_count')
    search_fields = ('hostel__name', 'room_number')

@admin.register(HostelMember)
class HostelMemberAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'check_in', 'check_out', 'is_active')
    search_fields = ('student__login_id',)
    readonly_fields = ('is_active',)
