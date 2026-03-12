from django.urls import path
from billing.webhooks import stripe_webhook
from .views import billing_dashboard, billing_portal
from . import views, webhooks

urlpatterns = [
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('dashboard/', billing_dashboard, name='billing_dashboard'),
    path('portal/', billing_portal, name='billing_portal'),
    path('create-checkout-session/<str:tier>/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook'),
    path("success/", views.billing_success, name="billing_success"),
    path("cancel/", views.billing_cancel, name="billing_cancel"),
]
