from django.db import models
from stores.models import Store

class Subscriber(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='subscribers')
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('store', 'email', 'phone')

    def __str__(self):
        return f"{self.name} ({self.store.name})"
