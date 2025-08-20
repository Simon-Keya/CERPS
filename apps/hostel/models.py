from django.db import models
from apps.users.models import User

class Hostel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_rooms(self):
        return self.rooms.count()

    total_rooms.short_description = "Total Rooms"

    def __str__(self):
        return self.name

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def occupants_count(self):
        return self.hostel_members.count()

    occupants_count.short_description = "Occupants"

    def __str__(self):
        return f"{self.room_number} ({self.hostel})"

class HostelMember(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hostel_memberships')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='hostel_members')
    check_in = models.DateField()
    check_out = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student} in {self.room}"
