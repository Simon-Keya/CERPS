from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Hostel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    total_rooms = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=1)
    occupants_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.hostel.name} - {self.room_number}"

class HostelMember(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.DateField(default=timezone.now)
    check_out = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        return self.check_out is None or self.check_out > timezone.now().date()

    def __str__(self):
        return f"{self.student.login_id} in {self.room}"
