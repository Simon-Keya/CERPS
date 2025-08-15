from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Hostel, Room, HostelMember
from .serializers import HostelSerializer, RoomSerializer, HostelMemberSerializer
from .permissions import IsHostelStaffOrReadOnly

class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [IsHostelStaffOrReadOnly]

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsHostelStaffOrReadOnly]

class HostelMemberViewSet(viewsets.ModelViewSet):
    queryset = HostelMember.objects.all()
    serializer_class = HostelMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_hostel_staff', False) or user.is_staff:
            return HostelMember.objects.all()
        return HostelMember.objects.filter(student=user)
