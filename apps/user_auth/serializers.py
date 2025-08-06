from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import (
    UserProfile, SocialAccount, IntegrationToken, GoogleCalendarIntegration,
    GoogleDocsIntegration, TelegramIntegration,
    AuthSession, UserActivity
)


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'phone_number', 'date_of_birth', 'avatar', 'bio',
            'timezone', 'language', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'profile']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        profile_data = validated_data.pop('profile', None)
        
        user = User.objects.create_user(**validated_data)
        
        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """User login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')

        return attrs


class SocialAccountSerializer(serializers.ModelSerializer):
    """Social account serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SocialAccount
        fields = [
            'id', 'user', 'provider', 'provider_account_id', 'provider_username',
            'provider_email', 'provider_name', 'provider_picture', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IntegrationTokenSerializer(serializers.ModelSerializer):
    """Integration token serializer"""
    user = UserSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = IntegrationToken
        fields = [
            'id', 'user', 'integration', 'access_token', 'refresh_token',
            'token_type', 'expires_at', 'scope', 'is_active', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
        }


class GoogleCalendarIntegrationSerializer(serializers.ModelSerializer):
    """Google Calendar integration serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GoogleCalendarIntegration
        fields = [
            'id', 'user', 'calendar_id', 'timezone', 'sync_enabled',
            'last_sync', 'sync_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GoogleDocsIntegrationSerializer(serializers.ModelSerializer):
    """Google Docs integration serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GoogleDocsIntegration
        fields = [
            'id', 'user', 'default_folder_id', 'auto_backup_enabled',
            'backup_frequency', 'last_backup', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TelegramIntegrationSerializer(serializers.ModelSerializer):
    """Telegram integration serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TelegramIntegration
        fields = [
            'id', 'user', 'telegram_user_id', 'telegram_username', 'chat_id',
            'notifications_enabled', 'notification_types', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']





class AuthSessionSerializer(serializers.ModelSerializer):
    """Auth session serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuthSession
        fields = [
            'id', 'user', 'session_key', 'ip_address', 'user_agent',
            'login_method', 'is_active', 'created_at', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']


class UserActivitySerializer(serializers.ModelSerializer):
    """User activity serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'activity_type', 'description', 'metadata',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GoogleOAuthSerializer(serializers.Serializer):
    """Google OAuth callback serializer"""
    code = serializers.CharField()
    state = serializers.CharField(required=False)
    scope = serializers.CharField(required=False)


class IntegrationConnectSerializer(serializers.Serializer):
    """Integration connection serializer"""
    integration = serializers.ChoiceField(choices=IntegrationToken.INTEGRATION_CHOICES)
    access_token = serializers.CharField()
    refresh_token = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)
    scope = serializers.CharField(required=False, allow_blank=True)


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Password reset serializer"""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer"""
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs 