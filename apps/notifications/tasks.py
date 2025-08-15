from celery import shared_task
from .models import Notification
from .services import send_email, send_sms
from django.utils import timezone

@shared_task
def process_notifications():
    notifications = Notification.objects.filter(sent=False)
    for notif in notifications:
        if notif.notif_type == 'EMAIL':
            send_email(notif.recipient.email, notif.title, notif.message)
        elif notif.notif_type == 'SMS':
            send_sms(notif.recipient.phone_number, notif.message)
        notif.sent = True
        notif.sent_at = timezone.now()
        notif.save()
