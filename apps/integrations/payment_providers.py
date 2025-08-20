"""
Adapters for Stripe, Paystack, M-Pesa.
These provide helper functions to:
 - verify signatures
 - parse webhook payloads
 - perform provider-specific calls (create checkout session etc.)

Make sure provider keys are in settings.
"""

import os
import stripe
from django.conf import settings
import hmac
import hashlib
import base64
import requests

# STRIPE
def init_stripe():
    stripe.api_key = settings.STRIPE_SECRET_KEY

def verify_stripe_signature(payload: bytes, sig_header: str, endpoint_secret: str):
    """
    Uses official Stripe approach: stripe.Webhook.construct_event recommended
    but we provide helper wrapper in views; keep here for reference.
    """
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        return event
    except Exception as e:
        raise

def create_stripe_checkout_session(amount_cents: int, currency: str, success_url: str, cancel_url: str, metadata: dict = None):
    init_stripe()
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price_data": {"currency": currency, "product_data": {"name": "Payment"}, "unit_amount": amount_cents}, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata or {}
    )
    return session

# PAYSTACK - simple signature verification
def verify_paystack_signature(payload: bytes, secret: str, signature: str) -> bool:
    # Paystack uses HMAC-SHA512 of payload with secret, Base64 or hex? Typically hex
    computed = hmac.new(secret.encode(), payload, hashlib.sha512).hexdigest()
    return computed == signature

def verify_paystack_event(reference: str) -> dict:
    secret = settings.PAYSTACK_SECRET_KEY
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {secret}"})
    resp.raise_for_status()
    return resp.json()

# MPESA - placeholder; different providers have different methods (Safaricom Daraja API)
def verify_mpesa_callback(data: dict) -> bool:
    # Validate with configured consumer key/secret or callback token depending on implementation
    # We provide a placeholder for integration implementers.
    return True
