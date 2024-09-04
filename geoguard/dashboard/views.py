import logging
from rest_framework.generics import ListAPIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from twilio.rest import Client
from decouple import config
from django.core.management import call_command
from rest_framework.permissions import IsAdminUser  
from rest_framework import permissions
from django.contrib import admin
from .models import CustomUser, Organization
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied




from .models import (
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
    CustomUser,
    Salary,
    Shift,
    UserSalary
)

from .serializers import (
    GeofencesSerializer, 
    UserGeofenceAssignmentSerializer, 
    UserLocationStatusGeofenceSerializer, 
    LocationHistorySerializer, 
    UserGeofencesSerializer, 
    OrganizationSerializer, 
    GroupOfOrganizationSerializer, 
    MonitoredUserTokenSerializer, 
    GeofenceGroupSerializer, 
    GeofenceGroupSettingsSerializer, 
    UserLocationStatusSerializer, 
    NotificationMethodsSerializer, 
    NotificationSettingsSerializer,
    CustomUserSerializer,
    MonitoredUserGeofencesSerializer,
    UserSalarySerializer
)
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError


# Import your CompanyFranchiseEntity model if it's not already imported
from .models import CustomUser

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        print("Data received:", data)  # Debug: Print entire request data

        # Check if 'organization' is in the data to determine if it's an admin creating their own account
        is_admin_creation = 'organization' in data
        organization = None

        if is_admin_creation:
            # Admin creating their own account
            organization_name = data.pop('organization')
            org = Organization.objects.create(name=organization_name)
            data['organization'] = org.id
            data['role'] = CustomUser.ADMIN
            organization = org
        else:
            # Admin creating a new user account
            request_user = request.user
            if request_user.is_anonymous:
                return Response({'error': 'Authentication required for creating new user accounts.'}, status=status.HTTP_403_FORBIDDEN)
            
            organization = request_user.organization
            data['organization'] = organization.id if organization else None

        serializer = CustomUserSerializer(data=data, context={'request': request, 'org': organization})

        if serializer.is_valid():
            print("Serializer valid")
            print("Data in create:", serializer.validated_data)  # Debug: Print validated data
            print("Salary data in create:", serializer.validated_data.get('salary'))  # Debug: Print salary data

            with transaction.atomic():
                user_instance = serializer.save()

                # Only handle salary and shifts if it's an admin creating a new user
                if not is_admin_creation:
                    salary_data = data.get('salary')
                    shifts_data = data.get('shifts', [])
                    
                    # Create salary if provided
                    if salary_data:
                        print("Creating salary:", salary_data)  # Debug: Print salary data being created
                        Salary.objects.create(**salary_data)
                    
                    # Create shifts if provided
                    for shift_data in shifts_data:
                        print("Creating shift:", shift_data)  # Debug: Print shift data being created
                        Shift.objects.create(user=user_instance, **shift_data)
                        call_command('update_location_and_salary')
                return Response({
                    'message': 'Signup information saved successfully. Awaiting approval.'
                    
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' and user.organization:
            return CustomUser.objects.filter(organization=user.organization)
        return CustomUser.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin' and user.organization:
            serializer.save(organization=user.organization)
        else:
            raise PermissionDenied("You do not have permission to create a user.")

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


# @admin.register(Signup)
# class SignupAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'created_at')
#     actions = ['approve_signup']

#     def approve_signup(self, request, queryset):
#         for signup in queryset:
#             user = CustomUser.objects.create_user(
#                 username=signup.username,
#                 password=signup.password,
#                 email=signup.email,
#                 first_name=signup.first_name,
#                 last_name=signup.last_name,
#                 contact=signup.contact,
#                 address1=signup.address1
#             )
#             organization = Organization.objects.create(name=signup.organization_name, owner=user)
#             token, created = Token.objects.get_or_create(user=user)
#             signup.delete()
#         self.message_user(request, "Selected signups have been approved and users created.")
#     approve_signup.short_description = "Approve selected signups"

logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                pass
        else:
            user = CustomUser.objects.filter(username=username).first()

        if user:
            # No need to check for Signup instance anymore
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                token, created = Token.objects.get_or_create(user=authenticated_user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)

        # Return a generic error message to prevent information leakage
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


logger = logging.getLogger(__name__)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info("Logout request received for user: %s", request.user)
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Logout failed: %s", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

# Usage in a view
class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user role
        user_role = user.role
        print(f"User role: {user_role}")

        return Response({
            'token': token.key,
            'role': user_role
        })


# class CustomUserListCreateAPIView(generics.ListCreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer
#     permission_classes = [AllowAny]  # Adjust permissions as necessary

#     def post(self, request, *args, **kwargs):
#         return SignupView.as_view()(request, *args, **kwargs)

class CustomUserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated] 
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    

class PolygonDataAPIView(APIView):
    def get(self, request):
        polygons = Geofences.objects.all()
        serializer = GeofencesSerializer(polygons, many=True)
        return Response(serializer.data)

class MonitoredUserListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(role=CustomUser.MONITORED)  # Filter users by role 'monitored'
    serializer_class = CustomUserSerializer

class GeofencesList(generics.ListCreateAPIView):
    queryset = Geofences.objects.all()
    serializer_class = GeofencesSerializer

class AssignGeofenceAPIView(generics.CreateAPIView):
    queryset = UserGeofenceAssignment.objects.all()
    serializer_class = UserGeofenceAssignmentSerializer

# class UserGeofencesAPIView(APIView):
#     def get(self, request, user_id=None):
#         if user_id is not None:
#             # Retrieve user geofences for a specific user
#             try:
#                 user = CustomUser.objects.get(id=user_id)
#                 user_geofences = UserGeofenceAssignment.objects.filter(user=user)
#                 serializer = UserGeofencesSerializer(user_geofences, many=True)
#                 return Response(serializer.data)
#             except CustomUser.DoesNotExist:
#                 return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             # Return all user geofences
#             user_geofences = UserGeofenceAssignment.objects.all()
#             serializer = UserGeofencesSerializer(user_geofences, many=True)
#             return Response(serializer.data)


class UserGeofencesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        user_geofences = UserGeofenceAssignment.objects.filter(user_id=user_id).values_list('geofence__id', flat=True)
        geofences = Geofences.objects.filter(id__in=user_geofences)
        serializer = GeofencesSerializer(geofences, many=True)  # Use your custom GeofencesSerializer
        return Response(serializer.data)

class AssignedGeofencesForMonitoredUsersAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MonitoredUserGeofencesSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            # Retrieve the monitored user with the provided user_id
            user = CustomUser.objects.get(id=user_id, role=CustomUser.MONITORED)
            # Return the geofence assignments for the monitored user
            return UserGeofenceAssignment.objects.filter(user=user)
        except CustomUser.DoesNotExist:
            # If the monitored user does not exist, return an empty queryset
            return UserGeofenceAssignment.objects.none()

# class UserLocationStatusAPIView(APIView):
#     # permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = UserLocationStatusSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Setup logging
logger = logging.getLogger(__name__)

# Load Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')

@method_decorator(csrf_exempt, name='dispatch')
class SendTwilioNotificationView(APIView):
    def post(self, request):
        to_phone_number = request.data.get('to')
        message_body = request.data.get('message')

        if not to_phone_number or not message_body:
            return Response({'error': 'Missing "to" or "message" parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the phone number is in E.164 format
        if not to_phone_number.startswith('+') or not to_phone_number[1:].isdigit():
            return Response({'error': 'Invalid phone number format. Must be in E.164 format.'}, status=status.HTTP_400_BAD_REQUEST)

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        try:
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone_number
            )
            logger.info(f"Message sent to {to_phone_number} with SID {message.sid}")
            return Response({'message_sid': message.sid}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to send message to {to_phone_number}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get an instance of a logger
logger = logging.getLogger(__name__)

class UserLocationStatusAPIView(generics.CreateAPIView):
    queryset = UserLocationStatus.objects.all()
    serializer_class = UserLocationStatusSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data

        # Manually extract token from request headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', "")
        if not auth_header.startswith('Token '):
            logger.error("Invalid token header. No credentials provided.")
            return Response({"detail": "Invalid token header. No credentials provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_key = auth_header.split('Token ')[-1]
        logger.debug(f"Extracted token: {token_key}")

        try:
            token = Token.objects.get(key=token_key)
            user = token.user
            logger.debug(f"Token belongs to user: {user.id}")  # Log user ID
        except Token.DoesNotExist:
            logger.error("Invalid token.")
            return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Add user ID to the data
        data['user_id'] = user.id
        logger.debug(f"User ID added to data: {data['user_id']}")

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.debug(f"UserLocationStatus created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLocationStatusListAPIView(generics.ListAPIView):
    serializer_class = UserLocationStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return UserLocationStatus.objects.filter(user_id=user_id)
        return UserLocationStatus.objects.all()

logger = logging.getLogger(__name__)

class LocationHistoryList(generics.ListCreateAPIView):
    serializer_class = LocationHistorySerializer
    permission_classes = []

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin' and user.organization:
            # Filter by user's organization
            return LocationHistory.objects.filter(user__organization=user.organization)
        else:
            # If not an admin or doesn't belong to an organization, show nothing
            return LocationHistory.objects.none()

    def create(self, request, *args, **kwargs):
        print("API Called")
        data = request.data

        # Manually extract token from request headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', "")
        if not auth_header.startswith('Token '):
            logger.error("Invalid token header. No credentials provided.")
            return Response({"detail": "Invalid token header. No credentials provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        token_key = auth_header.split('Token ')[-1]
        logger.debug(f"Extracted token: {token_key}")

        try:
            token = Token.objects.get(key=token_key)
            user = token.user
            logger.debug(f"Token belongs to user: {user.id}")  # Log user ID
        except Token.DoesNotExist:
            logger.error("Invalid token.")
            return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Add user to the data
        data['user'] = user.id
        logger.debug(f"User ID added to data: {data['user']}")

        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.debug(f"LocationHistory created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrganizationList(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Optional: Customize error handling if needed
    def handle_exception(self, exc):
        # Customize error response handling here
        return super().handle_exception(exc)

class GroupOfOrganizationList(generics.ListCreateAPIView):
    queryset = GroupOfOrganization.objects.all()
    serializer_class = GroupOfOrganizationSerializer

class MonitoredUserTokenList(generics.ListCreateAPIView):
    queryset = MonitoredUserToken.objects.all()
    serializer_class = MonitoredUserTokenSerializer

class GeofenceGroupList(generics.ListCreateAPIView):
    queryset = GeofenceGroup.objects.all()
    serializer_class = GeofenceGroupSerializer

class GeofenceGroupSettingsList(generics.ListCreateAPIView):
    queryset = GeofenceGroupSettings.objects.all()
    serializer_class = GeofenceGroupSettingsSerializer

class UserLocationStatusGeofenceList(generics.ListCreateAPIView):
    queryset = UserLocationStatusGeofence.objects.all()
    serializer_class = UserLocationStatusSerializer

class NotificationMethodsList(generics.ListCreateAPIView):
    queryset = NotificationMethods.objects.all()
    serializer_class = NotificationMethodsSerializer

class NotificationSettingsList(generics.ListCreateAPIView):
    queryset = NotificationSettings.objects.all()
    serializer_class = NotificationSettingsSerializer

logger = logging.getLogger(__name__)

class RunUpdateUserSalaries(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        user_ids = request.query_params.getlist('user_ids')

        try:
            # Log command execution
            logger.info('Running management command update_location_and_salary')
            call_command('update_location_and_salary')

            if user_ids:
                # Additional processing if needed
                pass

            return Response({'status': 'User salaries and locations updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error running update_location_and_salary: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CalculateUserSalaryAPIView(APIView):
    permission_classes = [IsAdminUser]  # Adjust permissions as needed

    def get(self, request, user_id):
        try:
            call_command('update_location_and_salary')

            # Calculate salary logic (you may call your management command here if needed)
            user_salary = UserSalary.objects.filter(user_id=user_id).first()
            
            if not user_salary:
                return Response({'error': 'User salary not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = UserSalarySerializer(user_salary)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error calculating user salary: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSalaryListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSalarySerializer

    def get_queryset(self):
        user = self.request.user
        
        if hasattr(user, 'organization'):
            return UserSalary.objects.filter(user__organization=user.organization)
        
        return UserSalary.objects.none()
