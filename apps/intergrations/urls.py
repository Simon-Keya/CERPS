from django.urls import path
from . import views

urlpatterns = [
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
]
