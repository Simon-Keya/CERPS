from celery import shared_task
from django.conf import settings
from .payment_providers import init_stripe
from apps.finance.models import Invoice, Payment
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_stripe_checkout_event(self, stripe_event):
    """
    Handle checkout.session.completed event payload (dict) asynchronously.
    """
    try:
        # Example: find invoice from metadata and create Payment record
        data = stripe_event.get("data", {}).get("object", {})
        metadata = data.get("metadata", {}) or {}
        invoice_id = metadata.get("invoice_id")
        if invoice_id:
            try:
                inv = Invoice.objects.get(pk=int(invoice_id))
                amount_total = int(data.get("amount_total", 0))
                Payment.objects.create(
                    invoice=inv,
                    provider="stripe",
                    provider_payment_id=data.get("id"),
                    amount_cents=amount_total,
                    status="completed",
                    raw=stripe_event
                )
                inv.status = "paid"
                inv.save()
            except Invoice.DoesNotExist:
                logger.warning("Invoice %s not found for stripe event", invoice_id)
    except Exception as exc:
        logger.exception("Failed to process stripe event: %s", exc)
        raise self.retry(exc=exc, countdown=10)
