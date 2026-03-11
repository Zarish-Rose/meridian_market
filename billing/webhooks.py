from datetime import datetime
import stripe
from django.http import HttpResponse
from django.conf import settings

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'invoice.paid':
        # grant platform access
        pass

    if event['type'] == 'customer.subscription.deleted':
        # revoke access
        pass

    if event['type'] == 'invoice.upcoming':
        # notify user
        pass

    return HttpResponse(status=200)

path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),

if event['type'] == 'customer.subscription.created':
    sub = event['data']['object']
    profile = Profile.objects.get(stripe_customer_id=sub['customer'])

    profile.stripe_subscription_id = sub['id']
    profile.subscription_tier = determine_tier_from_price(sub['items']['data'][0]['price']['id'])
    profile.trial_ends_at = datetime.fromtimestamp(sub['trial_end'])
    profile.is_subscribed = True
    profile.save()

# send email reminder when trial ends
if event['type'] == 'customer.subscription.trial_will_end':
    pass

# handle failed payments
if event['type'] == 'invoice.payment_failed':
    profile.is_subscribed = False
    profile.save()

# handle subscription cancellations
if event['type'] == 'customer.subscription.deleted':
    profile.is_subscribed = False
    profile.subscription_tier = 'free'
    profile.save()
