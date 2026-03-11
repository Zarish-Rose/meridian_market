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