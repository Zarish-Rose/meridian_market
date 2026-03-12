from django.urls import path
from billing.webhooks import stripe_webhook
from .views import billing_dashboard, customer_portal
from . import views, webhooks

urlpatterns = [
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('dashboard/', views.billing_dashboard, name='billing_dashboard'),
    path('portal/', views.customer_portal, name='customer_portal'),
    path('create-checkout-session/<str:tier>/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook'),
    path("success/", views.billing_success, name="billing_success"),
    path("cancel/", views.billing_cancel, name="billing_cancel"),
]
