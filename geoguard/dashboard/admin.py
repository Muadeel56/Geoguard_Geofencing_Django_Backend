from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, 
    Geofences, 
    UserGeofenceAssignment, 
    UserLocationStatus, 
    LocationHistory, 
    Organization, 
    GroupOfOrganization, 
    MonitoredUserToken, 
    GeofenceGroup, 
    GeofenceGroupSettings, 
    UserLocationStatusGeofence, 
    NotificationMethods, 
    NotificationSettings,
    OrganizationRole,
    Salary,
    UserSalary,
)

# Define a custom ModelAdmin for Signup
# class SignupAdmin(admin.ModelAdmin):
#     list_display = ['username', 'email', 'organization_name', 'is_approved']  # Adjust as per your needs
#     list_filter = ['is_approved']  # Add appropriate filters
#     search_fields = ('username', 'email', 'organization_name')

#     def get_queryset(self, request):
#         # Override queryset to include only non-approved signups
#         return Signup.objects.filter(is_approved=False)

#     def approve_signup(self, request, queryset):
#         # Custom action to approve selected signups
#         queryset.update(is_approved=True)

#     approve_signup.short_description = "Approve selected signups"

#     def reject_signup(self, request, queryset):
#         # Custom action to reject selected signups (optional)
#         queryset.delete()  # Example: Delete rejected signups

#     reject_signup.short_description = "Reject selected signups"

#     actions = [approve_signup, reject_signup]

# admin.site.register(Signup, SignupAdmin)

# Register other models as needed
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Geofences)
admin.site.register(UserGeofenceAssignment)
admin.site.register(UserLocationStatus)
admin.site.register(LocationHistory)
admin.site.register(Organization)
admin.site.register(GroupOfOrganization)
admin.site.register(MonitoredUserToken)
admin.site.register(GeofenceGroup)
admin.site.register(GeofenceGroupSettings)
admin.site.register(UserLocationStatusGeofence)
admin.site.register(NotificationMethods)
admin.site.register(NotificationSettings)
admin.site.register(OrganizationRole)
admin.site.register(Salary)
admin.site.register(UserSalary)
