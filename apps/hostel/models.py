from django.db import models
from django.utils import timezone

class Hostel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Floor(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='floors')
    number = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['hostel', 'number']
        ordering = ['number']

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('shared', 'Shared'),
    ]
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='single')
    capacity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['floor', 'number']
        ordering = ['number']

class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        unique_together = ['room', 'number']
        ordering = ['number']

class Student(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.registration_number})"

    class Meta:
        ordering = ['registration_number']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bookings')
    bed = models.OneToOneField(Bed, on_delete=models.CASCADE, related_name='booking')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.status == 'confirmed':
            self.bed.is_occupied = True
            self.bed.save()
        elif self.status == 'cancelled':
            self.bed.is_occupied = False
            self.bed.save()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']