from django.shortcuts import render, redirect
from django.conf import settings
import stripe

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
