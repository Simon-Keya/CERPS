from django.contrib import admin
from .models import Ledger, Invoice, Payment

@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = ('student', 'balance_cents', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('student__user__login_id',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'ledger', 'amount_cents', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'due_date')
    search_fields = ('ledger__student__user__login_id', 'description')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'amount_cents', 'payment_method', 'paid_at')
    list_filter = ('payment_method', 'paid_at')
    search_fields = ('invoice__ledger__student__user__login_id',)