from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HostelViewSet, RoomViewSet, HostelMemberViewSet

app_name = 'hostel'

router = DefaultRouter()
router.register(r'api/hostels', HostelViewSet, basename='hostel')
router.register(r'api/rooms', RoomViewSet, basename='room')
router.register(r'api/members', HostelMemberViewSet, basename='hostelmember')

urlpatterns = [
    path('', include(router.urls)),
]