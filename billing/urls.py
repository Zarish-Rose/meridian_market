from django.urls import path
from billing.webhooks import stripe_webhook
from . import views, webhooks

urlpatterns = [
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook'),
    path('dashboard/', views.billing_dashboard, name='billing_dashboard'),
    path('upgrade-required/', views.upgrade_required, name='upgrade_page'),
    path('billing-success/', views.billing_success, name='billing_success'),
    path('billing-cancel/', views.billing_cancel, name='billing_cancel'),
    path('credits/success/', views.credits_success, name='credits_success'),
    path('credits/cancel/', views.credits_cancel, name='credits_cancel'),
    path('credits/buy/', views.buy_credits, name='buy_credits'),
    path("change-plan/<str:new_tier>/", views.change_plan, name="change_plan"),
    path(
        'create-checkout-session/<str:tier>/<slug:store_slug>/',
        views.create_checkout_session,
        name='create_checkout_session',
    ),
    path("cancel/", views.cancel_subscription, name="cancel_subscription"),
    path('portal/', views.customer_portal, name='customer_portal'),
]
