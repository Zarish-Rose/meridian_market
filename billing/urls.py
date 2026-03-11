from django.urls import path
from billing.webhooks import stripe_webhook
from .views import billing_dashboard, billing_portal

urlpatterns = [
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('dashboard/', billing_dashboard, name='billing_dashboard'),
    path('portal/', billing_portal, name='billing_portal'),
]
