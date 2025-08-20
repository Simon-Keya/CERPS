from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.utils import log_action
from .models import Ledger, Invoice, Payment
from .serializers import LedgerSerializer, InvoiceSerializer, PaymentSerializer

class IsFinanceStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_superuser or request.user.groups.filter(name__in={'Finance', 'Registrar', 'SuperAdmin'}).exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_superuser or request.user.groups.filter(name__in={'Finance', 'Registrar', 'SuperAdmin'}).exists()

class LedgerViewSet(viewsets.ModelViewSet):
    queryset = Ledger.objects.select_related('student').all()
    serializer_class = LedgerSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student']
    search_fields = ['student__user__login_id']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'created_ledger', {'ledger_id': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'updated_ledger', {'ledger_id': instance.id})

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('ledger').all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ledger', 'status']
    search_fields = ['ledger__student__user__login_id', 'description']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'created_invoice', {'invoice_id': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'updated_invoice', {'invoice_id': instance.id})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('invoice').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['invoice', 'payment_method']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'created_payment', {'payment_id': instance.id})

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, 'updated_payment', {'payment_id': instance.id})