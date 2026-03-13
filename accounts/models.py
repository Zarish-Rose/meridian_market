from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username
    
    ROLE_CHOICES = [
    ('owner', 'Business Owner'),
    ('staff', 'Staff Member'),
    ('admin', 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')

    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free Trial'),
            ('basic', 'Basic'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    trial_ends_at = models.DateTimeField(blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    message_credits = models.IntegerField(default=0)
