from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.conf import settings
import json
import stripe
from .payment_providers import init_stripe, verify_paystack_signature, verify_paystack_event, verify_mpesa_callback
from .tasks import process_stripe_checkout_event
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)
init_stripe()

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as exc:
        logger.exception("Invalid stripe webhook: %s", exc)
        return HttpResponseBadRequest("invalid signature")
    # Process asynchronously
    process_stripe_checkout_event.delay(event)
    return HttpResponse(status=200)

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def paystack_webhook(request):
    # Paystack provides a signature header 'x-paystack-signature' (HMAC-SHA512)
    signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
    secret = getattr(settings, "PAYSTACK_SECRET_KEY", "")
    payload = request.body
    if not signature or not secret:
        logger.warning("Paystack signature or secret missing")
        return HttpResponseBadRequest("bad configuration")
    if not verify_paystack_signature(payload, secret, signature):
        return HttpResponseBadRequest("invalid signature")
    data = json.loads(payload.decode("utf-8"))
    # Example: handle charge.success
    event = data.get("event")
    if event == "charge.success":
        reference = data.get("data", {}).get("reference")
        # double-check with Paystack API
        try:
            result = verify_paystack_event(reference)
            # process result -> create Payment etc.
            logger.info("Paystack verified: %s", reference)
        except Exception:
            logger.exception("Failed paystack verify")
    return HttpResponse(status=200)

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_callback(request):
    # M-Pesa callback handling depends on provider
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("invalid json")
    if verify_mpesa_callback(data):
        # process payment
        return HttpResponse(status=200)
    return HttpResponseBadRequest("invalid callback")
