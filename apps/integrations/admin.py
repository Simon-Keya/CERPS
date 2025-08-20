from django.contrib import admin
from .models import (
    SMSGateway,
    EmailService,
    PaymentGatewayIntegration,
    WebhookLog,
    ExternalLTIIntegration,
)

admin.site.register(SMSGateway)
admin.site.register(EmailService)
admin.site.register(PaymentGatewayIntegration)
admin.site.register(WebhookLog)
admin.site.register(ExternalLTIIntegration)
