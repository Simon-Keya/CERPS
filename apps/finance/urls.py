from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LedgerViewSet, InvoiceViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'ledgers', LedgerViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]