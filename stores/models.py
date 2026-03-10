from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True)
    primary_color = models.CharField(max_length=7, blank=True, help_text="Hex code, e.g. #1A73E8")
    accent_color = models.CharField(max_length=7, blank=True, help_text="Hex code, e.g. #F4B400")

    def __str__(self):
        return self.name
    