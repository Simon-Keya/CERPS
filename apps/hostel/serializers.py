from rest_framework import serializers
from .models import Hostel, Room, HostelMember

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)

    class Meta:
        model = Room
        fields = '__all__'

class HostelMemberSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(source='student.login_id', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = HostelMember
        fields = ['id', 'student_id', 'room_number', 'check_in', 'check_out', 'is_active']
