from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User


class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True)
    primary_color = models.CharField(max_length=7, blank=True)
    accent_color = models.CharField(max_length=7, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_slug = self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.owner.username}-{self.name}")
        super().save(*args, **kwargs)

        self._original_slug = self.slug

    def __str__(self):
        return self.name

class StoreMember(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_memberships')
    role = models.CharField(max_length=20, choices=[
        ('staff', 'Staff Member'),
        ('manager', 'Manager'),
    ], default='staff')

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'user'], name='unique_store_user')
        ]

    def __str__(self):
        return f"{self.user.username} → {self.store.name}"
