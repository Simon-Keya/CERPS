from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ERP Modules
    path('api/users/', include('apps.users.urls')),
    path('api/admissions/', include('apps.admissions.urls')),
    path('api/academic/', include('apps.academic.urls')),
    path('api/core/', include('apps.core.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/hr/', include('apps.hr.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/hostel/', include('apps.hostel.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
    path('api/reporting/', include('apps.reporting.urls')),
]
