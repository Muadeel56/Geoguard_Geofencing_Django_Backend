from django.urls import path
from . import views
from .views import (
    CustomAuthToken, 
    CustomUserRetrieveUpdateDestroyAPIView, 
    AssignGeofenceAPIView, 
    MonitoredUserListAPIView, 
    UserGeofencesAPIView, 
    LoginView,
    AssignedGeofencesForMonitoredUsersAPIView,
    SendTwilioNotificationView,
    UserLocationStatusAPIView,
    UserLocationStatusListAPIView,
    RunUpdateUserSalaries,
    LogoutView,
    SignupView,
    UserSalaryListAPIView,
    CalculateUserSalaryAPIView
)

urlpatterns = [
    path('api/geofences/', views.GeofencesList.as_view(), name='geofences-list'),
    path('api/monitored-users/', MonitoredUserListAPIView.as_view(), name='monitored-users-list'),
    path('api/locationhistory/', views.LocationHistoryList.as_view(), name='location-history-list'),
    path('api/organization/', views.OrganizationList.as_view(), name='organization-list'),
    path('api/groupoforganization/', views.GroupOfOrganizationList.as_view(), name='group-of-organization-list'),
    path('api/monitoredusertoken/', views.MonitoredUserTokenList.as_view(), name='monitored-user-token-list'),
    path('api/geofencegroup/', views.GeofenceGroupList.as_view(), name='geofence-group-list'),
    path('api/geodencegroupsettings/', views.GeofenceGroupSettingsList.as_view(), name='geofence-group-settings-list'),
    path('api/notificationmethods/', views.NotificationMethodsList.as_view(), name='notification-methods-list'),
    path('api/notificationsettings/', views.NotificationSettingsList.as_view(), name='notification-settings-list'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/users/', views.UserListView.as_view(), name='user-list'),
    path('api/users/<int:pk>/', CustomUserRetrieveUpdateDestroyAPIView.as_view(), name='user-detail'),
    path('api/assign-geofence/', AssignGeofenceAPIView.as_view(), name='assign-geofence'),
    path('api/user-geofences/', views.UserGeofencesAPIView.as_view(), name='user-geofences'),
    path('api/user-geofences/<int:user_id>/', views.UserGeofencesAPIView.as_view(), name='user-geofences-detail'),
    path('api/user/<int:user_id>/geofences/', UserGeofencesAPIView.as_view(), name='user-geofences-specific'),
    path('api/user-location-status/', UserLocationStatusAPIView.as_view(), name='user-location-status-list'),
    path('api/assigned-geofences/', AssignedGeofencesForMonitoredUsersAPIView.as_view(), name='assigned-geofences'),
    path('api/assigned-geofences/<int:user_id>/', AssignedGeofencesForMonitoredUsersAPIView.as_view(), name='assigned-geofences'),
    path('api/send_twilio_notification/', SendTwilioNotificationView.as_view(), name='send_twilio_notification'),
    path('api/user-location-status-list/', UserLocationStatusListAPIView.as_view(), name='user-location-status-list-duplicate'),
    path('run-update-salaries/', RunUpdateUserSalaries.as_view(), name='run-update-salaries'),
    path('api/calculate-user-salary/<int:user_id>/', CalculateUserSalaryAPIView.as_view(), name='calculate-user-salary'),  # Add this line
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/signup/', SignupView.as_view(), name='api_signup'),
    path('api/user-salaries/', UserSalaryListAPIView.as_view(), name='user-salary-list'),
]
