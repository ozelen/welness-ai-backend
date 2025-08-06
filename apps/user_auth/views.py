from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from .models import (
    UserProfile, SocialAccount, IntegrationToken, GoogleCalendarIntegration,
    GoogleDocsIntegration, TelegramIntegration,
    UserActivity
)
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer, LoginSerializer,
    SocialAccountSerializer, IntegrationTokenSerializer, GoogleCalendarIntegrationSerializer,
    GoogleDocsIntegrationSerializer, TelegramIntegrationSerializer,
    GoogleOAuthSerializer, IntegrationConnectSerializer, PasswordChangeSerializer
)
from .services import GoogleOAuthService, GoogleCalendarService, GoogleDocsService, SocialAccountService


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            description='User registered',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            description='User logged in',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(generics.GenericAPIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='logout',
                description='User logged out',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile management"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            return UserProfile.objects.create(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Handle User model fields (first_name, last_name)
        user_data = {}
        profile_data = {}
        
        for key, value in request.data.items():
            if key in ['first_name', 'last_name']:
                user_data[key] = value
            else:
                profile_data[key] = value
        
        # Update User model if needed
        if user_data:
            user = request.user
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
        
        # Update UserProfile model
        serializer = self.get_serializer(instance, data=profile_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            description='Profile updated',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Return updated data
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GoogleOAuthView(generics.GenericAPIView):
    """Google OAuth authentication"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get Google OAuth URL"""
        try:
            oauth_service = GoogleOAuthService()
            auth_url = oauth_service.get_authorization_url()
            return Response({'auth_url': auth_url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Handle Google OAuth callback"""
        serializer = GoogleOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            oauth_service = GoogleOAuthService()
            tokens = oauth_service.exchange_code_for_tokens(serializer.validated_data['code'])
            user_info = oauth_service.get_user_info(tokens['access_token'])
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info['email'],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                }
            )
            
            # Create or update profile
            profile, profile_created = UserProfile.objects.get_or_create(user=user)
            
            # Store integration tokens
            for scope in tokens['scopes']:
                if 'calendar' in scope:
                    IntegrationToken.objects.update_or_create(
                        user=user,
                        integration='google_calendar',
                        defaults={
                            'access_token': tokens['access_token'],
                            'refresh_token': tokens.get('refresh_token'),
                            'scope': ','.join(tokens['scopes']),
                            'expires_at': timezone.now() + timezone.timedelta(hours=1),
                        }
                    )
                elif 'documents' in scope or 'drive' in scope:
                    IntegrationToken.objects.update_or_create(
                        user=user,
                        integration='google_docs',
                        defaults={
                            'access_token': tokens['access_token'],
                            'refresh_token': tokens.get('refresh_token'),
                            'scope': ','.join(tokens['scopes']),
                            'expires_at': timezone.now() + timezone.timedelta(hours=1),
                        }
                    )
            
            # Create social account
            SocialAccountService.create_social_account(user, 'google', {
                'id': user_info['id'],
                'email': user_info['email'],
                'name': f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip(),
                'picture': user_info.get('picture'),
            })
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'created': created
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleCalendarView(generics.GenericAPIView):
    """Google Calendar integration endpoints"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get calendar events"""
        try:
            calendar_service = GoogleCalendarService(request.user)
            events = calendar_service.get_events()
            return Response({'events': events})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Create calendar event"""
        try:
            calendar_service = GoogleCalendarService(request.user)
            event = calendar_service.create_event(
                summary=request.data.get('summary'),
                start_time=request.data.get('start_time'),
                end_time=request.data.get('end_time'),
                description=request.data.get('description', ''),
                location=request.data.get('location', '')
            )
            return Response({'event': event})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleDocsView(generics.GenericAPIView):
    """Google Docs integration endpoints"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List documents"""
        try:
            docs_service = GoogleDocsService(request.user)
            documents = docs_service.list_documents()
            return Response({'documents': documents})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Create document"""
        try:
            docs_service = GoogleDocsService(request.user)
            document = docs_service.create_document(
                title=request.data.get('title'),
                content=request.data.get('content', '')
            )
            return Response({'document': document})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TelegramIntegrationView(generics.GenericAPIView):
    """Telegram integration endpoints"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get Telegram integration status"""
        from .telegram_auth import TelegramAuthService
        status = TelegramAuthService.get_connection_status(request.user)
        return Response(status)

    def post(self, request):
        """Connect Telegram account"""
        try:
            from .telegram_auth import TelegramAuthService
            
            telegram_user_id = request.data.get('telegram_user_id')
            telegram_username = request.data.get('telegram_username')
            
            if not telegram_user_id:
                return Response({'error': 'telegram_user_id is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Connect user
            integration = TelegramAuthService.connect_user(
                user=request.user,
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username
            )
            
            return Response({
                'message': 'Telegram account connected successfully',
                'telegram_username': integration.telegram_username,
                'notifications_enabled': integration.notifications_enabled
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Disconnect Telegram account"""
        try:
            from .telegram_auth import TelegramAuthService
            
            success = TelegramAuthService.disconnect_user(request.user)
            
            if success:
                return Response({'message': 'Telegram account disconnected successfully'})
            else:
                return Response({'error': 'Telegram account not found'}, 
                              status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SocialAccountsView(generics.ListAPIView):
    """Social accounts management"""
    serializer_class = SocialAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user, is_active=True)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_social_account(request, provider):
    """Disconnect social account"""
    try:
        success = SocialAccountService.disconnect_social_account(request.user, provider)
        if success:
            return Response({'message': f'{provider} account disconnected'})
        else:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class IntegrationTokensView(generics.ListAPIView):
    """Integration tokens management"""
    serializer_class = IntegrationTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return IntegrationToken.objects.filter(user=self.request.user, is_active=True)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_integration(request):
    """Connect new integration"""
    serializer = IntegrationConnectSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        token_data = serializer.validated_data
        IntegrationToken.objects.update_or_create(
            user=request.user,
            integration=token_data['integration'],
            defaults={
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': token_data.get('expires_at'),
                'scope': token_data.get('scope'),
            }
        )
        
        return Response({'message': f'{token_data["integration"]} connected successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_integration(request, integration):
    """Disconnect integration"""
    try:
        token = IntegrationToken.objects.get(user=request.user, integration=integration)
        token.is_active = False
        token.save()
        
        return Response({'message': f'{integration} disconnected successfully'})
    except IntegrationToken.DoesNotExist:
        return Response({'error': 'Integration not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
