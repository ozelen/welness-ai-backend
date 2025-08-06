import hashlib
import time
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from django.contrib.auth.models import User
from .models import TelegramIntegration, UserActivity, SocialAccount

logger = logging.getLogger(__name__)


class TelegramAuthService:
    """Service for Telegram user identification and authentication"""
    
    @staticmethod
    def generate_connection_code(telegram_user_id: int) -> str:
        """Generate a unique connection code for Telegram user identification"""
        timestamp = int(time.time())
        code_data = f"{telegram_user_id}_{timestamp}_{settings.SECRET_KEY}"
        code_hash = hashlib.md5(code_data.encode()).hexdigest()[:8].upper()
        return code_hash
    
    @staticmethod
    def connect_user(user: User, telegram_user_id: int, 
                    telegram_username: str = None) -> TelegramIntegration:
        """Connect a Django user to their Telegram account"""
        integration, created = TelegramIntegration.objects.get_or_create(
            user=user,
            defaults={
                'telegram_user_id': telegram_user_id,
                'telegram_username': telegram_username,
                'chat_id': telegram_user_id,  # For direct messages, chat_id is the same as user_id
                'notifications_enabled': True,
                'notification_types': ['calendar_reminders', 'goal_updates', 'general']
            }
        )
        
        if not created:
            # Update existing integration
            integration.telegram_user_id = telegram_user_id
            integration.telegram_username = telegram_username
            integration.chat_id = telegram_user_id
            integration.save()
        
        # Create or update social account
        SocialAccount.objects.update_or_create(
            user=user,
            provider='telegram',
            defaults={
                'provider_account_id': str(telegram_user_id),
                'provider_username': telegram_username,
                'provider_name': f"Telegram User {telegram_user_id}",
                'is_active': True
            }
        )
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='social_account_connected',
            description='Connected Telegram account',
            metadata={
                'telegram_user_id': telegram_user_id,
                'telegram_username': telegram_username
            }
        )
        
        return integration
    
    @staticmethod
    def disconnect_user(user: User) -> bool:
        """Disconnect a user's Telegram account"""
        try:
            integration = TelegramIntegration.objects.get(user=user)
            integration.delete()
            
            # Deactivate social account
            try:
                social_account = SocialAccount.objects.get(user=user, provider='telegram')
                social_account.is_active = False
                social_account.save()
            except SocialAccount.DoesNotExist:
                pass
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='social_account_disconnected',
                description='Disconnected Telegram account'
            )
            
            return True
        except TelegramIntegration.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_by_telegram_id(telegram_user_id: int) -> Optional[User]:
        """Get Django user by Telegram user ID"""
        try:
            integration = TelegramIntegration.objects.get(telegram_user_id=telegram_user_id)
            return integration.user
        except TelegramIntegration.DoesNotExist:
            return None
    
    @staticmethod
    def get_telegram_integration(user: User) -> Optional[TelegramIntegration]:
        """Get Telegram integration for a Django user"""
        try:
            return TelegramIntegration.objects.get(user=user)
        except TelegramIntegration.DoesNotExist:
            return None
    
    @staticmethod
    def is_user_connected(telegram_user_id: int) -> bool:
        """Check if a Telegram user is connected to a Django account"""
        return TelegramIntegration.objects.filter(telegram_user_id=telegram_user_id).exists()
    
    @staticmethod
    def get_connection_status(user: User) -> Dict[str, Any]:
        """Get connection status for a user"""
        try:
            integration = TelegramIntegration.objects.get(user=user)
            return {
                'connected': True,
                'telegram_user_id': integration.telegram_user_id,
                'telegram_username': integration.telegram_username,
                'notifications_enabled': integration.notifications_enabled,
                'notification_types': integration.notification_types
            }
        except TelegramIntegration.DoesNotExist:
            return {'connected': False}


# Utility functions for use in bot handlers
def get_django_user_from_telegram(telegram_user_id: int) -> Optional[User]:
    """Get Django user from Telegram user ID - for use in bot handlers"""
    return TelegramAuthService.get_user_by_telegram_id(telegram_user_id)


def is_telegram_user_connected(telegram_user_id: int) -> bool:
    """Check if Telegram user is connected - for use in bot handlers"""
    return TelegramAuthService.is_user_connected(telegram_user_id)


def get_telegram_connection_code(telegram_user_id: int) -> str:
    """Generate connection code for Telegram user - for use in bot handlers"""
    return TelegramAuthService.generate_connection_code(telegram_user_id) 