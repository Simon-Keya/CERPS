from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notif_type', 'sent', 'created_at', 'sent_at')
    search_fields = ('title', 'recipient__login_id', 'message')
    readonly_fields = ('sent', 'sent_at')
