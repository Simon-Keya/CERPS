from django_filters import rest_framework as filters
from .models import Room, Booking

class RoomFilter(filters.FilterSet):
    hostel = filters.NumberFilter(field_name='floor__hostel__id')
    is_available = filters.BooleanFilter()

    class Meta:
        model = Room
        fields = ['hostel', 'room_type', 'is_available']

class BookingFilter(filters.FilterSet):
    student = filters.NumberFilter(field_name='student__id')
    status = filters.ChoiceFilter(choices=Booking.STATUS_CHOICES)

    class Meta:
        model = Booking
        fields = ['student', 'status']