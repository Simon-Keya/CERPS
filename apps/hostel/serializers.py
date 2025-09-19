from rest_framework import serializers
from .models import Hostel, Floor, Room, Bed, Student, Booking, Complaint
from django.utils import timezone
from apps.users.models import User  # This import is necessary for the ReadOnlyField source

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'address', 'capacity', 'is_active', 'created_at']

class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['id', 'hostel', 'number', 'description']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'floor', 'number', 'room_type', 'capacity', 'is_available']

class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = ['id', 'room', 'number', 'is_occupied']

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'registration_number', 'phone_number', 'created_at']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'student', 'bed', 'start_date', 'end_date', 'status', 'created_at']

class ComplaintSerializer(serializers.ModelSerializer):
    # This line is the key fix. It makes 'student' a read-only field for output.
    student = serializers.ReadOnlyField(source='student.user.login_id')

    class Meta:
        model = Complaint
        # 'student' is included in the fields for output but not required for input
        fields = ['id', 'student', 'title', 'description', 'status', 'created_at', 'resolved_at']
        # Also explicitly state that 'student' is read-only
        read_only_fields = ['student', 'resolved_at']

class CreateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['bed', 'start_date', 'end_date']

    def validate(self, data):
        bed = data['bed']
        if bed.is_occupied:
            raise serializers.ValidationError("This bed is already occupied.")
        return data

    def save(self, **kwargs):
        student = self.context['student']
        return super().save(student=student, status='pending', **kwargs)

class ResolveComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = []

    def save(self, **kwargs):
        complaint = self.instance
        if complaint.status == 'resolved':
            raise serializers.ValidationError("Complaint is already resolved.")
        complaint.status = 'resolved'
        complaint.resolved_at = timezone.now()
        complaint.save()
        return complaint