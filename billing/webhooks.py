import stripe
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Profile

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)


    # Subscription created or updated
    if event["type"] in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        status = subscription["status"]
        price_id = subscription["items"]["data"][0]["price"]["id"]

        # Find the user
        profile = Profile.objects.get(stripe_customer_id=customer_id)

        # Update your subscription model
        stripe.Subscription.objects.update_or_create(
            user=profile.user,
            defaults={
                "stripe_subscription_id": subscription["id"],
                "status": status,
                "price_id": price_id,
                "current_period_end": subscription["current_period_end"],
            }
        )

    # If payment fails
    if event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]

        profile = Profile.objects.get(stripe_customer_id=customer_id)

        # Mark subscription as unpaid or past_due
        stripe.Subscription.objects.filter(user=profile.user).update(
            status="past_due"
        )
    
    # Subscription cancellations
    if event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        profile = Profile.objects.get(stripe_customer_id=customer_id)

        stripe.Subscription.objects.filter(user=profile.user).update(
            status="canceled"
        )

    return HttpResponse(status=200)
