# Generated by Django 5.0.4 on 2024-07-23 15:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_alter_shift_end_shift_alter_shift_start_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='salary',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salary_info', to=settings.AUTH_USER_MODEL),
        ),
    ]
