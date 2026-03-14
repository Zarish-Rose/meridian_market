import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Store


@receiver(post_save, sender=Store)
def generate_store_qr(sender, instance, created, **kwargs):
    # Skip QR generation when explicitly disabled or when loading raw fixtures.
    if getattr(settings, "DISABLE_STORE_QR_GENERATION", False) or kwargs.get("raw", False):
        return

    # Prevent recursion when this signal saves only the qr_code field.
    update_fields = kwargs.get("update_fields")
    if update_fields and set(update_fields) == {"qr_code"}:
        return

    if not instance.slug:
        return

    # Only generate QR on creation or slug change
    if created or instance.slug != instance._original_slug:

        subscription_url = f"{settings.SITE_URL}/subscribe/{instance.slug}/"

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(str(subscription_url), optimize=0)

        try:
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
        except RecursionError:
            # Fallback path for rare recursion issues in qrcode polynomial math.
            img = qrcode.make(str(subscription_url))

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"{instance.slug}-qr.png"

        # Remove stale files so slug updates do not keep orphaned QR images.
        storage = instance.qr_code.storage
        upload_to = str(instance.qr_code.field.upload_to).strip("/")
        target_name = f"{upload_to}/{filename}" if upload_to else filename

        if instance.qr_code and instance.qr_code.name and instance.qr_code.name != target_name:
            if storage.exists(instance.qr_code.name):
                storage.delete(instance.qr_code.name)

        if storage.exists(target_name):
            storage.delete(target_name)

        instance.qr_code.save(filename, File(buffer), save=False)

        # Save ONLY the qr_code field to avoid recursion
        instance.save(update_fields=["qr_code"])
