from django.db import models
from django.utils import timezone


class SMSGateway(models.Model):
    """
    Stores SMS gateway configurations (e.g., Africa's Talking, Twilio).
    """
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=255)
    sender_id = models.CharField(max_length=50)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class EmailService(models.Model):
    """
    Stores email service provider configurations (e.g., Mailgun, SendGrid).
    """
    name = models.CharField(max_length=100, unique=True)
    smtp_host = models.CharField(max_length=255)
    smtp_port = models.IntegerField()
    username = models.EmailField()
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class PaymentGatewayIntegration(models.Model):
    """
    Stores general payment gateway integrations (e.g., MPesa, Stripe, PayPal).
    """
    GATEWAY_CHOICES = [
        ('mpesa', 'MPesa'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('pesapal', 'Pesapal'),
    ]

    name = models.CharField(max_length=100, unique=True)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    callback_url = models.URLField()
    is_active = models.BooleanField(default=True)
    last_synced = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_gateway_type_display()})"

    def sync(self):
        self.last_synced = timezone.now()
        self.save()


class WebhookLog(models.Model):
    """
    Logs webhook requests and responses for integrations.
    """
    source = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    response = models.TextField(blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        return f"{self.source} - {self.event_type} @ {self.received_at}"


class ExternalLTIIntegration(models.Model):
    """
    LTI integration model for connecting with external LMS platforms.
    """
    name = models.CharField(max_length=100, unique=True)
    platform_url = models.URLField()
    client_id = models.CharField(max_length=255)
    public_key = models.TextField(help_text="LTI public key or JWK")
    deployment_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "LTI Integration"
        verbose_name_plural = "LTI Integrations"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.platform_url})"
