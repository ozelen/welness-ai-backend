from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'user_auth'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Google OAuth
    path('google/', views.GoogleOAuthView.as_view(), name='google_oauth'),
    path('google/callback/', views.GoogleOAuthView.as_view(), name='google_callback'),
    
    # Google Calendar integration
    path('google/calendar/', views.GoogleCalendarView.as_view(), name='google_calendar'),
    
    # Google Docs integration
    path('google/docs/', views.GoogleDocsView.as_view(), name='google_docs'),
    
    # Telegram integration
    path('telegram/', views.TelegramIntegrationView.as_view(), name='telegram_integration'),
    
    # Social accounts
    path('social/', views.SocialAccountsView.as_view(), name='social_accounts'),
    path('social/<str:provider>/disconnect/', views.disconnect_social_account, name='disconnect_social'),
    
    # Integration tokens
    path('integrations/', views.IntegrationTokensView.as_view(), name='integration_tokens'),
    path('integrations/connect/', views.connect_integration, name='connect_integration'),
    path('integrations/<str:integration>/disconnect/', views.disconnect_integration, name='disconnect_integration'),
    
    # AllAuth URLs (for social authentication)
    path('allauth/', include('allauth.urls')),
] 