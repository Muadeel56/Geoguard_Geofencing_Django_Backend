# Generated by Django 5.0.4 on 2024-07-20 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_rename_mymodel_customuser_role_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salary',
            name='organization_role',
        ),
    ]
