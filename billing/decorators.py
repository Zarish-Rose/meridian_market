from time import time
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
import stripe
from urllib3 import request
from campaigns import models
from stores.models import Store

def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.profile.is_subscribed:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

# Metered monthly billing based on usage
stripe.UsageRecord.create(
    quantity=1,
    timestamp=int(time.time()),
    subscription_item='si_12345',  # from Stripe
    action='increment',
)

# Pre-paid credits when a pack is purchased
class MessageCredit(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

    if store.credits.balance <= 0:
        raise Exception("Not enough credits")
    store.credits.balance -= 1
    store.credits.save()

stripe.billing_portal.Session.create(
    customer=request.user.stripecustomer.stripe_customer_id,
    return_url='https://yourdomain.com/dashboard/',
)
<a href="{% url 'billing_portal' %}">Manage Billing</a>

def require_tier(min_tier):
    tier_order = ['free', 'basic', 'pro', 'enterprise']

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_tier = request.user.profile.subscription_tier
            if tier_order.index(user_tier) < tier_order.index(min_tier):
                return redirect('upgrade_page')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
