from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_id = serializers.CharField(source='recipient.login_id', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
