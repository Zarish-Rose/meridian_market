import uuid
from django.db import models
from django.utils import timezone

from encryption.fields import EncryptedCharField
from encryption.tokens import generate_token
from stores.models import Store


class Subscriber(models.Model):
    # Internal primary key (keep as integer for DB stability)
    id = models.BigAutoField(primary_key=True)

    # Public-facing UUID (safe for URLs, QR codes, external references)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Encrypted identity fields
    encrypted_phone = EncryptedCharField(max_length=255, null=True, blank=True)
    encrypted_birth_month = EncryptedCharField(max_length=255, null=True, blank=True)

    # Token for QR onboarding or secure lookups
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'email', 'phone')

    def save(self, *args, **kwargs):
        # Generate token only once
        if not self.token:
            self.token = generate_token()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Subscriber {self.uuid}"

class Subscription(models.Model):
    """
    Links a subscriber to a store.
    Supports seamless opt-in and opt-out.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("store", "subscriber")

    def unsubscribe(self):
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.subscriber} → {self.store} ({status})"
