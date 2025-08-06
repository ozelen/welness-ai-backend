from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, SocialAccount, IntegrationToken, GoogleCalendarIntegration,
    GoogleDocsIntegration, TelegramIntegration,
    AuthSession, UserActivity
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'timezone', 'language', 'created_at')
    list_filter = ('timezone', 'language', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_username', 'provider_email', 'is_active', 'created_at')
    list_filter = ('provider', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'provider_username', 'provider_email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(IntegrationToken)
class IntegrationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'integration', 'is_active', 'expires_at', 'created_at')
    list_filter = ('integration', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'integration')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(GoogleCalendarIntegration)
class GoogleCalendarIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'calendar_id', 'timezone', 'sync_enabled', 'sync_frequency', 'last_sync')
    list_filter = ('sync_enabled', 'sync_frequency', 'timezone')
    search_fields = ('user__username', 'user__email', 'calendar_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GoogleDocsIntegration)
class GoogleDocsIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'auto_backup_enabled', 'backup_frequency', 'last_backup')
    list_filter = ('auto_backup_enabled', 'backup_frequency')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TelegramIntegration)
class TelegramIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_username', 'telegram_user_id', 'notifications_enabled')
    list_filter = ('notifications_enabled', 'created_at')
    search_fields = ('user__username', 'user__email', 'telegram_username')
    readonly_fields = ('created_at', 'updated_at')





@admin.register(AuthSession)
class AuthSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'login_method', 'ip_address', 'is_active', 'created_at')
    list_filter = ('login_method', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'session_key', 'ip_address')
    readonly_fields = ('created_at', 'last_activity')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
