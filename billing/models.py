from django.contrib.auth.models import User
from django.db import models


class StripeSubscription(models.Model):
    TIER_CHOICES = [
        ("basic", "Basic"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    price_id = models.CharField(max_length=255, null=True, blank=True)
    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=50, null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.status in ["active", "trialing"]
