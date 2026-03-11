from django.db import models
from stores.models import Store

class Campaign(models.Model):
    MESSAGE_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email & SMS'),
        ('whatsapp', 'WhatsApp'),
        ('all', 'Email, SMS & WhatsApp'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=200)
    message = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='email')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(blank=True, null=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.store.name})"