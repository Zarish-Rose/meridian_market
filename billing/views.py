from django.shortcuts import render, redirect
from django.conf import settings
import stripe
from datetime import datetime

def create_subscription_checkout(request):
    customer = request.user.stripecustomer.stripe_customer_id

    session = stripe.checkout.Session.create(
        customer=customer,
        payment_method_types=['card'],
        mode='subscription',
        line_items=[{
            'price': 'price_12345',  # your Stripe price ID
            'quantity': 1,
        }],
        success_url='https://yourdomain.com/billing/success/',
        cancel_url='https://yourdomain.com/billing/cancel/',
    )

    return redirect(session.url)

def create_checkout_session(request, tier):
    price_map = {
        'basic': 'price_basic_monthly',
        'pro': 'price_pro_monthly',
    }

    session = stripe.checkout.Session.create(
        customer=request.user.profile.stripe_customer_id,
        mode='subscription',
        line_items=[{
            'price': price_map[tier],
            'quantity': 1,
        }],
        subscription_data={
            'trial_period_days': 14,
        },
        success_url='https://yourdomain.com/billing/success/',
        cancel_url='https://yourdomain.com/billing/cancel/',
    )

    return redirect(session.url)


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
