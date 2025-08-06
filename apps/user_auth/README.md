# Authentication & Integrations Module

A comprehensive Django authentication module that provides user registration, Google OAuth integration, and Telegram bot connectivity.

## Features

### 🔐 Authentication
- **User Registration & Login**: Traditional email/password authentication
- **JWT Token Authentication**: Secure token-based authentication with refresh tokens
- **Google OAuth**: Social authentication with Google accounts
- **Password Management**: Password change and reset functionality
- **Session Management**: Track user sessions and login history

### 🔗 Social Integrations
- **Google**: Full OAuth integration with Calendar and Docs access
- **Telegram**: Bot integration for notifications and interactions
- **Extensible**: Easy to add more social providers

### 📅 Google Services Integration
- **Google Calendar**: Create, read, update, and delete calendar events
- **Google Docs**: Create and manage documents
- **Google Drive**: File management and backup
- **OAuth Token Management**: Automatic token refresh and storage

### 🤖 Telegram User Identification
- **User Authentication**: Connect Telegram accounts to Django users
- **Connection Management**: Link/unlink Telegram accounts via API
- **Integration Ready**: Works with existing telegrinder bot setup
- **Connection Codes**: Secure user identification system

### 📊 User Management
- **User Profiles**: Extended user information with timezone and language preferences
- **Activity Tracking**: Comprehensive user activity logging
- **Admin Interface**: Full Django admin integration
- **API Endpoints**: RESTful API for all operations

## Models

### Core Models
- **UserProfile**: Extended user information (timezone, language, bio, etc.)
- **SocialAccount**: Social media account connections (Google, Telegram)
- **IntegrationToken**: OAuth tokens for Google integrations
- **AuthSession**: User session tracking
- **UserActivity**: Activity logging and analytics

### Integration Models
- **GoogleCalendarIntegration**: Calendar-specific settings
- **GoogleDocsIntegration**: Docs-specific settings
- **TelegramIntegration**: Telegram bot settings and notifications

## API Endpoints

### Authentication
```
POST /auth/register/          # User registration
POST /auth/login/            # User login
POST /auth/logout/           # User logout
POST /auth/token/refresh/    # Refresh JWT token
```

### User Profile
```
GET  /auth/profile/          # Get user profile
PUT  /auth/profile/          # Update user profile
```

### Google OAuth
```
GET  /auth/google/           # Get OAuth URL
POST /auth/google/callback/  # Handle OAuth callback
```

### Google Services
```
GET  /auth/google/calendar/  # Get calendar events
POST /auth/google/calendar/  # Create calendar event
GET  /auth/google/docs/      # List documents
POST /auth/google/docs/      # Create document
```

### Telegram Integration
```
GET  /auth/telegram/         # Get integration status
POST /auth/telegram/         # Connect Telegram account
DELETE /auth/telegram/       # Disconnect Telegram account
```

### Social Accounts
```
GET  /auth/social/           # List social accounts
POST /auth/social/{provider}/disconnect/  # Disconnect account
```

### Integrations
```
GET  /auth/integrations/     # List integration tokens
POST /auth/integrations/connect/  # Connect new integration
POST /auth/integrations/{integration}/disconnect/  # Disconnect integration
```

## Setup

### 1. Environment Variables
Add the following to your `.env` file:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback/

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Django Settings
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google+ API
   - Google Calendar API
   - Google Docs API
   - Google Drive API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Copy Client ID and Client Secret to environment variables

### 3. Telegram Integration Setup
1. Your existing `BOT_TOKEN` from `.env` will be used automatically
2. The auth module provides user identification services
3. Integrate with your existing telegrinder bot handlers

### 4. Database Migrations
```bash
python manage.py makemigrations user_auth
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Integrate with Existing Bot
```python
# In your bot handlers, import the auth utilities
from user_auth.telegram_auth import (
    get_django_user_from_telegram,
    is_telegram_user_connected,
    get_telegram_connection_code
)

# Example usage in a bot handler
if is_telegram_user_connected(message.from_user.id):
    django_user = get_django_user_from_telegram(message.from_user.id)
    # User is authenticated, proceed with functionality
```

## Usage Examples

### User Registration
```python
import requests

# Register new user
response = requests.post('http://localhost:8000/auth/register/', {
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'secure_password',
    'password_confirm': 'secure_password',
    'first_name': 'John',
    'last_name': 'Doe',
    'profile': {
        'phone_number': '+1234567890',
        'timezone': 'America/New_York',
        'language': 'en'
    }
})

# Get tokens
tokens = response.json()['tokens']
access_token = tokens['access']
```

### Google Calendar Integration
```python
import requests
from datetime import datetime, timedelta

headers = {'Authorization': f'Bearer {access_token}'}

# Get calendar events
response = requests.get('http://localhost:8000/auth/google/calendar/', headers=headers)
events = response.json()['events']

# Create calendar event
event_data = {
    'summary': 'Team Meeting',
    'start_time': datetime.now().isoformat(),
    'end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
    'description': 'Weekly team sync',
    'location': 'Conference Room A'
}

response = requests.post('http://localhost:8000/auth/google/calendar/', 
                        json=event_data, headers=headers)
```

### Telegram Integration
```python
# Connect Telegram account
telegram_data = {
    'telegram_user_id': 123456789,
    'telegram_username': 'john_doe'
}

response = requests.post('http://localhost:8000/auth/telegram/', 
                        json=telegram_data, headers=headers)

# Get integration status
response = requests.get('http://localhost:8000/auth/telegram/', headers=headers)
status = response.json()
```

### Telegram Bot Commands
Users can interact with the bot using these commands:
- `/start` - Welcome message and main menu
- `/connect` - Connect Telegram account to Wellness AI
- `/disconnect` - Unlink Telegram account
- `/profile` - View profile information
- `/help` - Show help message

## Services

### GoogleOAuthService
Handles Google OAuth authentication flow:
- Generate authorization URLs
- Exchange codes for tokens
- Get user information

### GoogleCalendarService
Manages Google Calendar operations:
- List calendars and events
- Create, update, delete events
- Automatic token refresh

### GoogleDocsService
Manages Google Docs operations:
- Create and update documents
- List user documents
- Document content management

### TelegramAuthService
Manages Telegram user identification:
- User connection/disconnection
- Connection status checking
- Integration management
- Works with existing telegrinder bot

### SocialAccountService
Manages social account connections:
- Connect/disconnect social accounts
- Update account information
- Activity logging

## Security Features

- **JWT Token Authentication**: Secure token-based authentication
- **Token Refresh**: Automatic token refresh mechanism
- **Token Blacklisting**: Secure logout with token invalidation
- **CORS Protection**: Cross-origin request protection
- **Activity Logging**: Comprehensive security audit trail
- **OAuth PKCE**: Enhanced OAuth security with PKCE

## Admin Interface

The module provides a comprehensive Django admin interface for:
- User management with inline profiles
- Social account management
- Integration token monitoring
- Activity tracking and analytics
- Google service configurations
- Telegram integration settings

## Extending the Module

### Adding New Social Providers
1. Add provider to `SocialAccount.PROVIDER_CHOICES`
2. Create provider-specific integration model if needed
3. Add OAuth configuration to settings
4. Create provider-specific service class
5. Add API endpoints

### Adding New Integrations
1. Add integration to `IntegrationToken.INTEGRATION_CHOICES`
2. Create integration-specific model if needed
3. Create service class for the integration
4. Add API endpoints
5. Update admin interface

## Testing

Run tests with:
```bash
python manage.py test user_auth
```

## Contributing

1. Follow Django coding standards
2. Add tests for new features
3. Update documentation
4. Ensure all migrations work correctly

## License

This module is part of the Wellness AI project and follows the same license terms. 