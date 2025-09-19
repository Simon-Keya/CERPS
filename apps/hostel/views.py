import logging
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Hostel, Floor, Room, Bed, Student, Booking, Complaint
from .serializers import (
    HostelSerializer, FloorSerializer, RoomSerializer, BedSerializer,
    StudentSerializer, BookingSerializer, ComplaintSerializer,
    CreateBookingSerializer, ResolveComplaintSerializer
)
from .permissions import IsHostelAdmin, IsStudentOrHostelAdmin
from .filters import RoomFilter, BookingFilter

logger = logging.getLogger(__name__)

class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address']
    ordering = ['-created_at']

class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.select_related('hostel').all()
    serializer_class = FloorSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hostel']
    ordering = ['number']

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('floor__hostel').all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RoomFilter
    search_fields = ['number']
    ordering = ['number']

class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.select_related('room__floor__hostel').all()
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'is_occupied']
    ordering = ['number']

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['registration_number', 'user__username', 'user__email']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('student__user', 'bed__room__floor__hostel').all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BookingFilter
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        logger.debug(f"BookingViewSet.get_queryset for user: {user}")
        if user.is_superuser or user.groups.filter(name__in=['HostelAdmin', 'SuperAdmin']).exists():
            return qs
        try:
            student = Student.objects.get(user=user)
            return qs.filter(student=student)
        except Student.DoesNotExist:
            return qs.none()

    @action(detail=False, methods=['post'], url_path='create-booking', permission_classes=[permissions.IsAuthenticated, IsStudentOrHostelAdmin])
    def create_booking(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CreateBookingSerializer(data=request.data, context={'student': student})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.select_related('student__user').all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOrHostelAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        logger.debug(f"ComplaintViewSet.get_queryset for user: {user}")
        if user.is_superuser or user.groups.filter(name__in=['HostelAdmin', 'SuperAdmin']).exists():
            return qs
        try:
            student = Student.objects.get(user=user)
            return qs.filter(student=student)
        except Student.DoesNotExist:
            return qs.none()
    
    # Corrected method to perform creation and link to student
    def perform_create(self, serializer):
        student = Student.objects.get(user=self.request.user)
        serializer.save(student=student)

    @action(detail=True, methods=['post'], url_path='resolve', permission_classes=[permissions.IsAuthenticated, IsHostelAdmin])
    def resolve_complaint(self, request, pk=None):
        complaint = self.get_object()
        serializer = ResolveComplaintSerializer(complaint, data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        complaint = serializer.save()
        return Response(ComplaintSerializer(complaint).data, status=status.HTTP_200_OK)