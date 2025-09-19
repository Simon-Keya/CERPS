from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet, FloorViewSet, RoomViewSet, BedViewSet,
    StudentViewSet, BookingViewSet, ComplaintViewSet
)

router = DefaultRouter()
router.register(r'hostels', HostelViewSet, basename='hostel')
router.register(r'floors', FloorViewSet, basename='floor')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'beds', BedViewSet, basename='bed')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'complaints', ComplaintViewSet, basename='complaint')

urlpatterns = [
    path('', include(router.urls)),
]
