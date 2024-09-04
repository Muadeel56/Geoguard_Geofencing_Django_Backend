# Generated by Django 5.0.4 on 2024-07-20 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_shift'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='end_day',
            field=models.CharField(default='Sunday', max_length=10),
        ),
        migrations.AddField(
            model_name='organization',
            name='start_day',
            field=models.CharField(default='Saturday', max_length=10),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
