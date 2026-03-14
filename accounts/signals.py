from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings
import stripe

from .models import Profile

stripe.api_key = settings.STRIPE_SECRET_KEY

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def create_stripe_customer(sender, instance, created, **kwargs):
    if created:
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=instance.user.email,
            name=instance.user.username,
        )
        instance.stripe_customer_id = customer.id
        instance.save()        
