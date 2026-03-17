# Generated migration to rename Subscription model to StripeSubscription

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subscription',
            new_name='StripeSubscription',
        ),
    ]
