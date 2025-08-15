from rest_framework import serializers

class StripeWebhookSerializer(serializers.Serializer):
    # We don't enforce fields because Stripe payloads vary; use this to log/validate minimal fields optionally
    id = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    data = serializers.JSONField(required=False)
