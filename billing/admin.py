from django.contrib import admin
from billing.models import StripeSubscription

# Register your models here.
admin.site.register(StripeSubscription)