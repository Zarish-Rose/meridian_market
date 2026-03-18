import stripe
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from billing.utils import can_send_messages, plan_summary
from stores.models import Store

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    "basic": settings.STRIPE_PRICE_BASIC,
    "pro": settings.STRIPE_PRICE_PRO,
    "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
}


def _get_primary_store(user):
    profile = user.profile

    if profile.role == "owner":
        return Store.objects.filter(owner=user).first()
    if profile.role in ["staff", "manager"]:
        return Store.objects.filter(members__user=user).distinct().first()
    if profile.role == "admin":
        return Store.objects.first()

    return None


def _get_recent_invoices(customer_id):
    if not customer_id:
        return []

    try:
        invoices = stripe.Invoice.list(customer=customer_id, limit=10)
    except stripe.error.StripeError:
        return []

    return [
        {
            "created_at": datetime.fromtimestamp(invoice.created),
            "total": (invoice.total or 0) / 100,
            "currency": (invoice.currency or "").upper(),
            "status": invoice.status,
            "hosted_invoice_url": getattr(invoice, "hosted_invoice_url", None),
        }
        for invoice in invoices.data
    ]


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


def billing(request):
    profile = request.user.profile
    subscription = getattr(request.user, "subscription", None)
    store = _get_primary_store(request.user)
    summary = plan_summary(request.user)
    invoices = _get_recent_invoices(profile.stripe_customer_id)

    context = {
        "subscription": subscription,
        "summary": summary,
        "store": store,
        "invoices": invoices,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, "billing/billing_portal.html", context)


def customer_portal(request):
    profile = request.user.profile

    session = stripe.billing_portal.Session.create(
        customer=profile.stripe_customer_id,
        return_url=request.build_absolute_uri(reverse("billing")),
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
        return redirect("billing")

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

    return redirect("billing")
    # Subscription update


def cancel_subscription(request):
    profile = request.user.profile
    subscription = get_stripe_subscription(profile)

    stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=True
    )

    return redirect("billing")
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


def billing_success(request):
    return render(request, "billing/billing_success.html")


def billing_cancel(request):
    return render(request, "billing/billing_cancel.html")


def credits_success(request):
    return render(request, "billing/credits_success.html")


def credits_cancel(request):
    return render(request, "billing/credits_cancel.html")


def send_message(request):
    if not can_send_messages(request.user):
        return redirect("upgrade_page")
    # Message logic


def upgrade_required(request):
    return render(request, "billing/upgrade_required.html")
