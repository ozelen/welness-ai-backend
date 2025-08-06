import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .models import (
    IntegrationToken, GoogleCalendarIntegration, GoogleDocsIntegration,
    UserActivity, SocialAccount
)


class GoogleOAuthService:
    """Service for handling Google OAuth authentication"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive',
    ]
    
    def __init__(self):
        self.client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)
        self.redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', None)
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Google OAuth credentials not configured")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get Google OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        if state:
            flow.state = state
            
        return flow.authorization_url()[0]
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        flow.fetch_token(code=code)
        
        return {
            'access_token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes,
        }
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        credentials = Credentials(access_token)
        service = build('oauth2', 'v2', credentials=credentials)
        
        user_info = service.userinfo().get().execute()
        return user_info


class GoogleCalendarService:
    """Service for Google Calendar integration"""
    
    def __init__(self, user: User):
        self.user = user
        self.token = self._get_token('google_calendar')
        if not self.token:
            raise ValueError("Google Calendar integration not found")
    
    def _get_token(self, integration: str) -> Optional[IntegrationToken]:
        """Get integration token for user"""
        return IntegrationToken.objects.filter(
            user=self.user,
            integration=integration,
            is_active=True
        ).first()
    
    def _get_credentials(self) -> Credentials:
        """Get Google credentials from stored token"""
        if self.token.is_expired() and self.token.refresh_token:
            credentials = Credentials(
                token=self.token.access_token,
                refresh_token=self.token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=self.token.scope.split(',') if self.token.scope else []
            )
            
            if credentials.expired:
                credentials.refresh(Request())
                self.token.access_token = credentials.token
                self.token.save()
        else:
            credentials = Credentials(self.token.access_token)
        
        return credentials
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of user's calendars"""
        credentials = self._get_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        
        try:
            calendar_list = service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            raise Exception(f"Failed to get calendars: {error}")
    
    def get_events(self, calendar_id: str = 'primary', 
                   time_min: Optional[datetime] = None,
                   time_max: Optional[datetime] = None,
                   max_results: int = 10) -> List[Dict[str, Any]]:
        """Get calendar events"""
        credentials = self._get_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=7)
        
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            raise Exception(f"Failed to get events: {error}")
    
    def create_event(self, summary: str, start_time: datetime, end_time: datetime,
                     description: str = '', location: str = '', calendar_id: str = 'primary') -> Dict[str, Any]:
        """Create a new calendar event"""
        credentials = self._get_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        
        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        try:
            event = service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            # Log activity
            UserActivity.objects.create(
                user=self.user,
                activity_type='integration_connected',
                description=f'Created calendar event: {summary}',
                metadata={'event_id': event['id'], 'calendar_id': calendar_id}
            )
            
            return event
        except HttpError as error:
            raise Exception(f"Failed to create event: {error}")
    
    def update_event(self, event_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing calendar event"""
        credentials = self._get_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        
        try:
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            for key, value in kwargs.items():
                if key in ['summary', 'description', 'location']:
                    event[key] = value
                elif key in ['start', 'end']:
                    event[key] = {
                        'dateTime': value.isoformat(),
                        'timeZone': 'UTC',
                    }
            
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return updated_event
        except HttpError as error:
            raise Exception(f"Failed to update event: {error}")
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """Delete a calendar event"""
        credentials = self._get_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        
        try:
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return True
        except HttpError as error:
            raise Exception(f"Failed to delete event: {error}")


class GoogleDocsService:
    """Service for Google Docs integration"""
    
    def __init__(self, user: User):
        self.user = user
        self.token = self._get_token('google_docs')
        if not self.token:
            raise ValueError("Google Docs integration not found")
    
    def _get_token(self, integration: str) -> Optional[IntegrationToken]:
        """Get integration token for user"""
        return IntegrationToken.objects.filter(
            user=self.user,
            integration=integration,
            is_active=True
        ).first()
    
    def _get_credentials(self) -> Credentials:
        """Get Google credentials from stored token"""
        if self.token.is_expired() and self.token.refresh_token:
            credentials = Credentials(
                token=self.token.access_token,
                refresh_token=self.token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=self.token.scope.split(',') if self.token.scope else []
            )
            
            if credentials.expired:
                credentials.refresh(Request())
                self.token.access_token = credentials.token
                self.token.save()
        else:
            credentials = Credentials(self.token.access_token)
        
        return credentials
    
    def create_document(self, title: str, content: str = '') -> Dict[str, Any]:
        """Create a new Google Doc"""
        credentials = self._get_credentials()
        docs_service = build('docs', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        try:
            # Create document
            document = {
                'title': title
            }
            doc = docs_service.documents().create(body=document).execute()
            
            # Add content if provided
            if content:
                requests = [
                    {
                        'insertText': {
                            'location': {
                                'index': 1
                            },
                            'text': content
                        }
                    }
                ]
                docs_service.documents().batchUpdate(
                    documentId=doc['documentId'],
                    body={'requests': requests}
                ).execute()
            
            # Log activity
            UserActivity.objects.create(
                user=self.user,
                activity_type='integration_connected',
                description=f'Created Google Doc: {title}',
                metadata={'document_id': doc['documentId']}
            )
            
            return doc
        except HttpError as error:
            raise Exception(f"Failed to create document: {error}")
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get document content"""
        credentials = self._get_credentials()
        service = build('docs', 'v1', credentials=credentials)
        
        try:
            document = service.documents().get(documentId=document_id).execute()
            return document
        except HttpError as error:
            raise Exception(f"Failed to get document: {error}")
    
    def update_document(self, document_id: str, content: str) -> Dict[str, Any]:
        """Update document content"""
        credentials = self._get_credentials()
        service = build('docs', 'v1', credentials=credentials)
        
        try:
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': 1
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }
            ]
            
            result = service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return result
        except HttpError as error:
            raise Exception(f"Failed to update document: {error}")
    
    def list_documents(self, query: str = '') -> List[Dict[str, Any]]:
        """List user's documents"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        try:
            query_params = "mimeType='application/vnd.google-apps.document'"
            if query:
                query_params += f" and name contains '{query}'"
            
            results = service.files().list(
                q=query_params,
                pageSize=20,
                fields="nextPageToken, files(id, name, createdTime, modifiedTime)"
            ).execute()
            
            return results.get('files', [])
        except HttpError as error:
            raise Exception(f"Failed to list documents: {error}")


class SocialAccountService:
    """Service for managing social accounts"""
    
    @staticmethod
    def create_social_account(user: User, provider: str, provider_data: Dict[str, Any]) -> SocialAccount:
        """Create or update social account"""
        social_account, created = SocialAccount.objects.get_or_create(
            user=user,
            provider=provider,
            defaults={
                'provider_account_id': provider_data.get('id'),
                'provider_username': provider_data.get('username'),
                'provider_email': provider_data.get('email'),
                'provider_name': provider_data.get('name'),
                'provider_picture': provider_data.get('picture'),
            }
        )
        
        if not created:
            # Update existing account
            for field, value in provider_data.items():
                if hasattr(social_account, f'provider_{field}'):
                    setattr(social_account, f'provider_{field}', value)
            social_account.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='integration_connected',
            description=f'Connected {provider} account',
            metadata={'provider': provider, 'account_id': provider_data.get('id')}
        )
        
        return social_account
    
    @staticmethod
    def disconnect_social_account(user: User, provider: str) -> bool:
        """Disconnect social account"""
        try:
            social_account = SocialAccount.objects.get(user=user, provider=provider)
            social_account.is_active = False
            social_account.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='integration_disconnected',
                description=f'Disconnected {provider} account',
                metadata={'provider': provider}
            )
            
            return True
        except SocialAccount.DoesNotExist:
            return False
    
    @staticmethod
    def get_user_social_accounts(user: User) -> List[SocialAccount]:
        """Get all social accounts for user"""
        return SocialAccount.objects.filter(user=user, is_active=True) 