from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.contrib.gis.db import models as gis_models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime


class Organization(models.Model):
    name = models.CharField(max_length=255)
    start_day = models.CharField(max_length=10, default="Monday")
    end_day = models.CharField(max_length=10, default="Friday")

    def __str__(self):
        return f"{self.name}: Working days from {self.start_day} to {self.end_day}"

class CustomUser(AbstractUser):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)

    ADMIN = 'admin'
    MONITORED = 'monitored'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MONITORED, 'Monitored')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    salary = models.OneToOneField('Salary', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

class Salary(models.Model):
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"User: {self.user.username}, Basic Pay: {self.basic_pay}, Allowances: {self.allowances}"

class Shift(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shifts')
    start_shift = models.TimeField()
    end_shift = models.TimeField()

    def __str__(self):
        return f"{self.user.username}: {self.start_shift} to {self.end_shift}"

class Geofences(gis_models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    shape = gis_models.PolygonField()

    def __str__(self):
        return self.name

class UserGeofenceAssignment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    geofence = models.ForeignKey(Geofences, on_delete=models.CASCADE)

class UserLocationStatus(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)
    geofence = models.ForeignKey(Geofences, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.timestamp}"

class LocationHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    record_at = models.DateTimeField(auto_now=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_within_geofence = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.record_at} - Lat: {self.latitude}, Lon: {self.longitude}"

@receiver(post_save, sender=LocationHistory)
def check_geofence(sender, instance, **kwargs):
    geofences = Geofences.objects.all()
    point = Point(instance.longitude, instance.latitude)
    
    is_within = False
    for geofence in geofences:
        if geofence.shape.contains(point):
            is_within = True
            UserLocationStatus.objects.update_or_create(
                user=instance.user,
                geofence=geofence,
                defaults={'status': 'Inside', 'timestamp': timezone.now()}
            )
            break
    
    if not is_within:
        UserLocationStatus.objects.update_or_create(
            user=instance.user,
            geofence=None,  # No geofence associated
            defaults={'status': 'Outside', 'timestamp': timezone.now()}
        )
    
    # Update the LocationHistory record
    instance.is_within_geofence = is_within
    instance.save(update_fields=['is_within_geofence'])

class GroupOfOrganization(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class MonitoredUserToken(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

class GeofenceGroup(models.Model):
    geofence = models.ForeignKey(Geofences, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)

class GeofenceGroupSettings(models.Model):
    geofence_group_id = models.ForeignKey(GeofenceGroup, on_delete=models.CASCADE)
    notification_threshold = models.FloatField()

class UserLocationStatusGeofence(models.Model):
    user_location_status = models.ForeignKey(UserLocationStatus, on_delete=models.CASCADE)
    geofence_group = models.ForeignKey(GeofenceGroup, on_delete=models.CASCADE)

class NotificationMethods(models.Model):
    SMS = 'sms'
    EMAIL = 'email'
    PUSH = 'push'

    METHOD_CHOICES = [
        (SMS, 'SMS'),
        (EMAIL, 'Email'),
        (PUSH, 'Push Notification')
    ]
    type = models.CharField(max_length=20, choices=METHOD_CHOICES)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

class NotificationSettings(models.Model):
    geofence_group_settings_id = models.ForeignKey(GeofenceGroupSettings, on_delete=models.CASCADE)
    notification_threshold = models.FloatField()
    notification_methods = models.ForeignKey(NotificationMethods, on_delete=models.CASCADE)

class OrganizationRole(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.organization.name} - {self.role_name}"

class UserSalary(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_salary')
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    month = models.IntegerField(default=timezone.now().month)
    year = models.IntegerField(default=timezone.now().year)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.salary}"
