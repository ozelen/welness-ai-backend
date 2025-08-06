from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import timezone
from django.core.exceptions import ValidationError
import json


class UserProfile(models.Model):
    """Extended user profile with basic user information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"

    class Meta:
        db_table = 'user_auth_user_profile'


class SocialAccount(models.Model):
    """Model to store additional social account information"""
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('telegram', 'Telegram'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_account_id = models.CharField(max_length=255, unique=True)
    provider_username = models.CharField(max_length=255, blank=True, null=True)
    provider_email = models.EmailField(blank=True, null=True)
    provider_name = models.CharField(max_length=255, blank=True, null=True)
    provider_picture = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_auth_social_account'
        unique_together = ['user', 'provider']

    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class IntegrationToken(models.Model):
    """Model to store OAuth tokens for various integrations"""
    INTEGRATION_CHOICES = [
        ('google_calendar', 'Google Calendar'),
        ('google_docs', 'Google Docs'),
        ('google_drive', 'Google Drive'),
        ('telegram_bot', 'Telegram Bot'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integration_tokens')
    integration = models.CharField(max_length=30, choices=INTEGRATION_CHOICES)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_type = models.CharField(max_length=20, default='Bearer')
    expires_at = models.DateTimeField(blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_auth_integration_token'
        unique_together = ['user', 'integration']

    def __str__(self):
        return f"{self.user.email} - {self.integration}"

    def is_expired(self):
        """Check if the token is expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def get_token_data(self):
        """Return token data as dictionary"""
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'scope': self.scope,
        }


class GoogleCalendarIntegration(models.Model):
    """Specific model for Google Calendar integration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_calendar')
    calendar_id = models.CharField(max_length=255, default='primary')
    timezone = models.CharField(max_length=50, default='UTC')
    sync_enabled = models.BooleanField(default=True)
    last_sync = models.DateTimeField(blank=True, null=True)
    sync_frequency = models.CharField(
        max_length=20,
        choices=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='daily'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_auth_google_calendar_integration'

    def __str__(self):
        return f"{self.user.email} - Google Calendar"


class GoogleDocsIntegration(models.Model):
    """Specific model for Google Docs integration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_docs')
    default_folder_id = models.CharField(max_length=255, blank=True, null=True)
    auto_backup_enabled = models.BooleanField(default=False)
    backup_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    last_backup = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_auth_google_docs_integration'

    def __str__(self):
        return f"{self.user.email} - Google Docs"


class TelegramIntegration(models.Model):
    """Specific model for Telegram integration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_integration')
    telegram_user_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    chat_id = models.BigIntegerField()
    notifications_enabled = models.BooleanField(default=True)
    notification_types = models.JSONField(default=list)  # ['meal_reminders', 'goal_updates', etc.]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_auth_telegram_integration'

    def __str__(self):
        return f"{self.user.email} - Telegram"





class AuthSession(models.Model):
    """Model to track user sessions and login history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    login_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('google', 'Google'),
            ('telegram', 'Telegram'),
        ],
        default='email'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_auth_session'

    def __str__(self):
        return f"{self.user.email} - {self.session_key}"


class UserActivity(models.Model):
    """Model to track user activities and engagement"""
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('account_created', 'Account Created'),
        ('password_changed', 'Password Changed'),
        ('email_verified', 'Email Verified'),
        ('integration_connected', 'Integration Connected'),
        ('integration_disconnected', 'Integration Disconnected'),
        ('social_account_connected', 'Social Account Connected'),
        ('social_account_disconnected', 'Social Account Disconnected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_auth_user_activity'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.created_at}"
