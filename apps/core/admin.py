from django.contrib import admin
from .models import AuditLog

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('action', 'user__username')
    list_filter = ('timestamp',)

admin.site.register(AuditLog, AuditLogAdmin)