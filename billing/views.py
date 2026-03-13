from ast import Store

import stripe
from datetime import datetime, time
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from billing.utils import can_send_messages, has_enterprise, has_pro
from accounts.models import Profile
from stores.models import Store

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    "basic": settings.STRIPE_PRICE_BASIC,
    "pro": settings.STRIPE_PRICE_PRO,
    "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
}

def create_checkout_session(request, tier, store_slug):
    store = get_object_or_404(Store, slug=store_slug)
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
        metadata={
            "store_id": store.id,
            "store_slug": store.slug,
        },
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

def get_stripe_subscription(profile):
    sub = stripe.Subscription.list(
        customer=profile.stripe_customer_id,
        status="all",
        limit=1
    )
    if sub.data:
        return sub.data[0]
    return None
    # Retrieves the user's current subscription

def change_plan(request, new_tier):
    profile = request.user.profile
    subscription = get_stripe_subscription(profile)

    if not subscription:
        return redirect("billing_dashboard")

    new_price_id = PLAN_PRICE_MAP.get(new_tier)

    stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=False,  # change immediately
        proration_behavior="create_prorations",
        items=[{
            "id": subscription["items"]["data"][0].id,
            "price": new_price_id,
        }],
    )

    return redirect("billing_dashboard")
    # Subscription update

def cancel_subscription(request):
    profile = request.user.profile
    subscription = get_stripe_subscription(profile)

    stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=True
    )

    return redirect("billing_dashboard")
    # Cancel subscription

def buy_credits(request):
    profile = request.user.profile

    checkout_session = stripe.checkout.Session.create(
        customer=profile.stripe_customer_id,
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price": settings.STRIPE_PRICE_MESSAGE_CREDITS,
            "quantity": 1,
        }],
        success_url=request.build_absolute_uri(reverse("credits_success")),
        cancel_url=request.build_absolute_uri(reverse("credits_cancel")),
    )

    return redirect(checkout_session.url)

def send_message(request):
    profile = request.user.profile

    if profile.message_credits <= 0:
        return redirect("buy_credits")

    profile.message_credits -= 1
    profile.save()
    # Deduct credit when user sends a message

    stripe.UsageRecord.create(
    quantity=1,
    timestamp=int(time.time()),
    action="increment",
    subscription_item=subscription_item_id,
    )
    # Metered monthly billing based on usage

def send_message(request):
    if not can_send_messages(request.user):
        return redirect("upgrade_page")
    # Message logic

def upgrade_required(request):
    return render(request, "billing/upgrade_required.html")
