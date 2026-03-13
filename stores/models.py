import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files import File
from django.utils.text import slugify
from django.contrib.auth.models import User

class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.owner.username}-{self.name}")
        super().save(*args, **kwargs)
        # Ensures QR code is generated after store creation

        subscription_url = f"{settings.SITE_URL}/subscribe/{self.slug}/"

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )
        qr.add_data(subscription_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save to ImageField
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        file_name = f"{self.slug}-qr.png"

        self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)
    
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True)
    primary_color = models.CharField(max_length=7, blank=True, help_text="Hex code, e.g. #1A73E8")
    accent_color = models.CharField(max_length=7, blank=True, help_text="Hex code, e.g. #F4B400")

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
        unique_together = ('store', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.store.name}"
