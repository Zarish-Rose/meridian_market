from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            'stores',
            '0004_alter_storemember_unique_together_store_qr_code_and_more',
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='accent_color',
        ),
        migrations.RemoveField(
            model_name='store',
            name='logo',
        ),
        migrations.RemoveField(
            model_name='store',
            name='primary_color',
        ),
        migrations.RemoveField(
            model_name='store',
            name='tagline',
        ),
    ]
