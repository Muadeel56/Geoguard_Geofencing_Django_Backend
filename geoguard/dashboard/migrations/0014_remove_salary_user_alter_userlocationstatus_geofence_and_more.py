# Generated by Django 5.0.4 on 2024-07-24 08:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_salary_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salary',
            name='user',
        ),
        migrations.AlterField(
            model_name='userlocationstatus',
            name='geofence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.geofences'),
        ),
        migrations.AlterField(
            model_name='usersalary',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_salary', to=settings.AUTH_USER_MODEL),
        ),
    ]
