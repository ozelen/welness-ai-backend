from datetime import datetime, timedelta
from django.utils import timezone


class GoogleCalendarService:
    """Service for Google Calendar integration"""
    
    def __init__(self, user):
        self.user = user
        # TODO: Add Google OAuth integration
        # self.credentials = self._get_user_credentials()
        # self.service = self._build_calendar_service()
    
    def _get_user_credentials(self):
        """Get user's Google OAuth credentials"""
        # TODO: Implement OAuth flow
        # This would store/retrieve user's Google OAuth tokens
        pass
    
    def _build_calendar_service(self):
        """Build Google Calendar API service"""
        # TODO: Implement Google Calendar API client
        # from googleapiclient.discovery import build
        # return build('calendar', 'v3', credentials=self.credentials)
        pass
    
    def create_event(self, meal):
        """Create Google Calendar event for meal"""
        if not meal.is_scheduled:
            return None
        
        # TODO: Implement actual Google Calendar API call
        event_data = self._prepare_event_data(meal)
        
        # Placeholder for actual API call
        # event = self.service.events().insert(
        #     calendarId='primary',
        #     body=event_data
        # ).execute()
        
        # For now, just return a mock event ID
        mock_event_id = f"mock_event_{meal.id}_{int(timezone.now().timestamp())}"
        
        # Update meal with calendar event ID
        meal.google_calendar_event_id = mock_event_id
        meal.last_synced_to_calendar = timezone.now()
        meal.save()
        
        return mock_event_id
    
    def update_event(self, meal):
        """Update existing Google Calendar event"""
        if not meal.google_calendar_event_id:
            return self.create_event(meal)
        
        # TODO: Implement actual Google Calendar API call
        event_data = self._prepare_event_data(meal)
        
        # Placeholder for actual API call
        # event = self.service.events().update(
        #     calendarId='primary',
        #     eventId=meal.google_calendar_event_id,
        #     body=event_data
        # ).execute()
        
        meal.last_synced_to_calendar = timezone.now()
        meal.save()
        
        return meal.google_calendar_event_id
    
    def delete_event(self, meal):
        """Delete Google Calendar event"""
        if not meal.google_calendar_event_id:
            return True
        
        # TODO: Implement actual Google Calendar API call
        # self.service.events().delete(
        #     calendarId='primary',
        #     eventId=meal.google_calendar_event_id
        # ).execute()
        
        # Clear the event ID
        meal.google_calendar_event_id = ""
        meal.last_synced_to_calendar = timezone.now()
        meal.save()
        
        return True
    
    def _prepare_event_data(self, meal):
        """Prepare event data for Google Calendar API"""
        # Convert string date to date object if needed
        if isinstance(meal.start_date, str):
            start_date = datetime.strptime(meal.start_date, '%Y-%m-%d').date()
        else:
            start_date = meal.start_date
            
        # Handle time field
        if isinstance(meal.start_time, str):
            start_time = datetime.strptime(meal.start_time, '%H:%M:%S').time()
        else:
            start_time = meal.start_time or datetime.min.time()
            
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = start_datetime + timedelta(minutes=meal.duration_minutes)
        
        event_data = {
            'summary': f"Meal: {meal.name}",
            'description': f"Diet: {meal.diet.name}\nType: {meal.get_meal_type_display()}\nCalories: {meal.get_total_calories():.0f}",
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC'
            },
            'colorId': meal.get_calendar_color_id(),
        }
        
        # Add recurrence if specified
        if meal.recurrence_type != 'none':
            recurrence = self._generate_recurrence_rule(meal)
            if recurrence:
                event_data['recurrence'] = [recurrence]
        
        return event_data
    
    def _generate_recurrence_rule(self, meal):
        """Generate Google Calendar recurrence rule"""
        if meal.recurrence_type == 'daily':
            rule = 'RRULE:FREQ=DAILY'
        elif meal.recurrence_type == 'weekly':
            rule = 'RRULE:FREQ=WEEKLY'
        elif meal.recurrence_type == 'weekday':
            rule = 'RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR'
        elif meal.recurrence_type == 'weekend':
            rule = 'RRULE:FREQ=WEEKLY;BYDAY=SA,SU'
        elif meal.recurrence_type == 'custom':
            # For custom, we'll need additional fields in the future
            # For now, treat as weekly
            rule = 'RRULE:FREQ=WEEKLY'
        else:
            return None
        
        if meal.recurrence_until:
            rule += f';UNTIL={meal.recurrence_until.strftime("%Y%m%d")}'
        
        return rule
    
    def sync_from_calendar(self):
        """Future: Sync events from Google Calendar back to app"""
        # This is where bi-directional sync will be implemented
        # For now, this is a placeholder for future development
        pass


def sync_meal_to_calendar(meal):
    """Helper function to sync a meal to Google Calendar"""
    service = GoogleCalendarService(meal.diet.user)
    
    if meal.is_scheduled:
        if meal.google_calendar_event_id:
            return service.update_event(meal)
        else:
            return service.create_event(meal)
    else:
        if meal.google_calendar_event_id:
            return service.delete_event(meal)
        return None
