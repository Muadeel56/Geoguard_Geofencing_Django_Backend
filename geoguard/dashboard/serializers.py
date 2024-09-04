from rest_framework import serializers
from .models import (
    Geofences, UserGeofenceAssignment, UserLocationStatus, LocationHistory, 
    Organization, GroupOfOrganization, MonitoredUserToken, GeofenceGroup, 
    GeofenceGroupSettings, UserLocationStatusGeofence, NotificationMethods, 
    NotificationSettings, CustomUser, Salary, Shift, UserSalary
)
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.utils import timezone


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['basic_pay', 'allowances']

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['start_shift', 'end_shift']

    def validate(self, data):
        if data.get('start_shift') and data.get('end_shift'):
            if data['end_shift'] <= data['start_shift']:
                raise serializers.ValidationError("End shift must be after start shift.")
        return data


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    salary = SalarySerializer(required=False)
    shifts = ShiftSerializer(many=True, required=False)
    user_salary = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'firstName', 'lastName', 'email', 'contact', 'username',
            'password', 'address1', 'address2', 'role', 'organization',
            'salary', 'shifts', 'user_salary'
        ]

    def get_salary(self, obj):
        if obj.salary:
            return {
                'basic_pay': obj.salary.basic_pay,
                'allowances': obj.salary.allowances
            }
        return None

    def get_user_salary(self, obj):
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        try:
            user_salary = UserSalary.objects.get(user=obj, month=current_month, year=current_year)
            return UserSalarySerializer(user_salary).data
        except UserSalary.DoesNotExist:
            return None

    def create(self, validated_data):
        salary_data = validated_data.pop('salary', None)
        shifts_data = validated_data.pop('shifts', [])
        password = validated_data.pop('password')
        organization = self.context.get('org')

        user = CustomUser.objects.create(**validated_data)

        if organization:
            user.organization = organization
        user.save()

        if password:
            user.set_password(password)
            user.save()

        if salary_data:
            salary = Salary.objects.create(**salary_data)
            user.salary = salary
            user.save()

        for shift_data in shifts_data:
            Shift.objects.create(user=user, **shift_data)

        return user


    def validate(self, data):
        return data

class GeofencesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Geofences
        fields = '__all__'
        geo_field = 'shape'

    def to_representation(self, instance):
        return super().to_representation(instance)


class OrganizationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name']


class UserSalarySerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    salary = SalarySerializer()
    organization = serializers.SerializerMethodField()

    class Meta:
        model = UserSalary
        fields = ['user', 'salary', 'bonus', 'month', 'year', 'monthly_salary', 'organization']

    def get_organization(self, obj):
        if obj.organization:
            return OrganizationNameSerializer(obj.organization).data
        return None




class UserGeofenceAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGeofenceAssignment
        fields = '__all__'


class UserGeofencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGeofenceAssignment
        fields = ['user', 'geofence']


class MonitoredUserGeofencesSerializer(serializers.ModelSerializer):
    geofences = serializers.SerializerMethodField()

    class Meta:
        model = UserGeofenceAssignment
        fields = ['id', 'geofences']

    def get_geofences(self, obj):
        geofences = UserGeofenceAssignment.objects.filter(user=obj.user).select_related('geofence')
        return GeofencesSerializer([assignment.geofence for assignment in geofences], many=True).data


class UserLocationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationStatus
        fields = '__all__'


class LocationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationHistory
        fields = '__all__'


class GroupOfOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupOfOrganization
        fields = '__all__'


class MonitoredUserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoredUserToken
        fields = '__all__'


class GeofenceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeofenceGroup
        fields = '__all__'


class GeofenceGroupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeofenceGroupSettings
        fields = '__all__'


class UserLocationStatusGeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationStatusGeofence
        fields = '__all__'


class NotificationMethodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationMethods
        fields = '__all__'


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = '__all__'
