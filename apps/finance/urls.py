from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LedgerViewSet, InvoiceViewSet, PaymentViewSet

app_name = 'finance'

router = DefaultRouter()
router.register(r'api/ledgers', LedgerViewSet, basename='ledger')
router.register(r'api/invoices', InvoiceViewSet, basename='invoice')
router.register(r'api/payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]