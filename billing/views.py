import stripe
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from billing.utils import has_enterprise, has_pro
from accounts.models import Profile

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

def send_message(request):
    user = request.user

    if not (has_pro(user) or has_enterprise(user)):
        return redirect("upgrade_page")
    # Feature logic here

def billing_dashboard(request):
    profile = request.user.profile
    subscription = getattr(request.user, "subscription", None)

    # Fetch invoices from Stripe
    invoices = stripe.Invoice.list(customer=profile.stripe_customer_id, limit=10)

    context = {
        "subscription": subscription,
        "invoices": invoices.data,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, "billing/dashboard.html", context)

def customer_portal(request):
    profile = request.user.profile

    session = stripe.billing_portal.Session.create(
        customer=profile.stripe_customer_id,
        return_url=request.build_absolute_uri(reverse("billing_dashboard")),
    )

    return redirect(session.url)

def billing_success(request):
    return render(request, "billing/success.html")

def billing_cancel(request):
    return render(request, "billing/cancel.html")

