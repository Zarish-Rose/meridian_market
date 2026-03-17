from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ("owner", "Business Owner"),
        ("manager", "Manager"),
        ("staff", "Staff Member"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="owner",
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    message_credits = models.IntegerField(default=0)

    def __str__(self):
        return self.full_name or self.user.username
