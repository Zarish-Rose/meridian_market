import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    "basic": settings.STRIPE_PRICE_BASIC,
    "pro": settings.STRIPE_PRICE_PRO,
    "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
}

def create_checkout_session(request, tier):
    profile = request.user.profile
    price_id = PLAN_PRICE_MAP.get(tier)

    if not price_id:
        return JsonResponse({"error": "Invalid plan"}, status=400)

    checkout_session = stripe.checkout.Session.create(
        customer=profile.stripe_customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        success_url=request.build_absolute_uri(
            reverse("billing_success")
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("billing_cancel")),
    )

    return redirect(checkout_session.url)

def billing_success(request):
    return render(request, "billing/success.html")

def billing_cancel(request):
    return render(request, "billing/cancel.html")

def billing_dashboard(request):
    profile = request.user.profile
    stripe_customer = profile.stripe_customer_id

    # Fetch invoices from Stripe
    invoices = stripe.Invoice.list(customer=stripe_customer, limit=10)

    # Fetch subscription details
    subscription = None
    if profile.stripe_subscription_id:
        subscription = stripe.Subscription.retrieve(profile.stripe_subscription_id)

    # Fetch usage (if using metered billing)
    usage = None
    if subscription:
        items = subscription['items']['data']
        for item in items:
            if item['price']['recurring']['usage_type'] == 'metered':
                usage = stripe.UsageRecordSummary.list(
                    subscription_item=item['id']
                )

    return render(request, 'billing/dashboard.html', {
        'profile': profile,
        'subscription': subscription,
        'invoices': invoices,
        'usage': usage,
    })

def billing_portal(request):
    session = stripe.billing_portal.Session.create(
        customer=request.user.profile.stripe_customer_id,
        return_url='https://yourdomain.com/billing/dashboard/',
    )
    return redirect(session.url)
