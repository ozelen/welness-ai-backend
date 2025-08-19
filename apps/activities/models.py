from django.db import models
from django.contrib.auth.models import User
from typing import Dict, Any, Optional


class Exercise(models.Model):
    """Exercises that can be used in activities"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, help_text='Category like "Cardio", "Strength", "Flexibility"')
    muscle_groups = models.CharField(max_length=200, blank=True, help_text='Primary muscle groups targeted')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='intermediate')
    equipment_needed = models.CharField(max_length=200, blank=True, help_text='Equipment required for this exercise')
    calories_per_hour_per_kg = models.FloatField(help_text='Calories burned per hour per kg of body weight', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_personal = models.BooleanField(default=False, help_text='Personal exercise created by user')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text='User who created this exercise (null for system defaults)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_exercise'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'muscle_groups': self.muscle_groups,
            'difficulty_level': self.difficulty_level,
            'equipment_needed': self.equipment_needed,
            'calories_per_hour_per_kg': self.calories_per_hour_per_kg,
            'is_active': self.is_active,
            'is_personal': self.is_personal,
        }


class ActivityType(models.Model):
    """Types of activities (from deficits.csv)"""
    name = models.CharField(max_length=100, unique=True, help_text='Internal name (e.g., "running")')
    display_name = models.CharField(max_length=100, help_text='User-friendly name (e.g., "Running")')
    calories_per_hour_per_kg = models.FloatField(help_text='Calories burned per hour per kg of body weight')
    category = models.CharField(max_length=50, choices=[
        ('cardio', 'Cardio'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ], default='other')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    exercise_schema = models.JSONField(default=dict, blank=True, help_text='JSON Schema for exercise details in this activity type')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activities_activity_type'
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return f"{self.display_name} ({self.category})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'calories_per_hour_per_kg': self.calories_per_hour_per_kg,
            'category': self.category,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'exercise_schema': self.exercise_schema,
        }


class Activity(models.Model):
    """Planned activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planned_activities')
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True, help_text='Custom name for this activity')
    duration_hours = models.FloatField(help_text='Planned duration in hours')
    
    # Calendar scheduling
    is_scheduled = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text="End date for recurrent activities")
    start_time = models.TimeField(null=True, blank=True)
    
    # Recurrence options
    RECURRENCE_TYPES = [
        ('none', 'No Recurrence'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('weekday', 'Weekdays (Mon-Fri)'),
        ('weekend', 'Weekends (Sat-Sun)'),
        ('custom', 'Custom Days'),
    ]
    recurrence_type = models.CharField(max_length=10, choices=RECURRENCE_TYPES, default='none')
    recurrence_until = models.DateField(null=True, blank=True)
    recurrence_days = models.CharField(max_length=50, blank=True, null=True, help_text='Comma-separated days for custom recurrence (e.g., "mon,tue,thu,fri")')
    
    # Google Calendar integration
    google_calendar_event_id = models.CharField(max_length=255, blank=True)
    last_synced_to_calendar = models.DateTimeField(null=True, blank=True)
    
    # Activity status
    is_completed = models.BooleanField(default=False, help_text='Whether this planned activity was completed')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_activity'
        ordering = ['-start_date', '-created_at']
    
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.user.username} - {self.name or self.activity_type.display_name} ({self.duration_hours}h) on {self.start_date}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'activity_type': self.activity_type.to_dict(),
            'duration_hours': self.duration_hours,
            'is_scheduled': self.is_scheduled,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'recurrence_type': self.recurrence_type,
            'recurrence_until': self.recurrence_until.isoformat() if self.recurrence_until else None,
            'recurrence_days': self.recurrence_days,
            'is_completed': self.is_completed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def get_calendar_color_id(self):
        """Get Google Calendar color ID based on activity type category"""
        color_map = {
            'cardio': '1',        # Blue
            'strength': '2',      # Green
            'flexibility': '3',   # Purple
            'sports': '4',        # Red
            'other': '5',         # Yellow
        }
        return color_map.get(self.activity_type.category, '1')
    
    def generate_rrule(self):
        """Generate Google Calendar recurrence rule"""
        if self.recurrence_type == 'none':
            return None
        
        if self.recurrence_type == 'daily':
            return {'freq': 'DAILY'}
        
        if self.recurrence_type == 'weekly':
            return {'freq': 'WEEKLY'}
        
        if self.recurrence_type == 'weekday':
            return {'freq': 'WEEKLY', 'byday': ['MO', 'TU', 'WE', 'TH', 'FR']}
        
        if self.recurrence_type == 'weekend':
            return {'freq': 'WEEKLY', 'byday': ['SA', 'SU']}
        
        if self.recurrence_type == 'custom' and self.recurrence_days:
            # Convert custom days to Google Calendar format
            day_mapping = {
                'mon': 'MO', 'tue': 'TU', 'wed': 'WE', 'thu': 'TH', 
                'fri': 'FR', 'sat': 'SA', 'sun': 'SU'
            }
            custom_days = []
            for day in self.recurrence_days.lower().split(','):
                day = day.strip()
                if day in day_mapping:
                    custom_days.append(day_mapping[day])
            if custom_days:
                return {'freq': 'WEEKLY', 'byday': custom_days}
        
        return None
    
    @property
    def calories_burned(self) -> Optional[float]:
        """Calculate calories burned based on activity type and duration"""
        if not self.activity_type.calories_per_hour_per_kg:
            return None
        
        # Get user weight (you might want to get this from user profile)
        # For now, using a default weight of 70kg
        user_weight_kg = 70.0
        
        # Calculate calories: calories_per_hour_per_kg * weight * duration_hours
        calories = self.activity_type.calories_per_hour_per_kg * user_weight_kg * self.duration_hours
        return round(calories, 1)


class ActivityExercise(models.Model):
    """Exercises within an activity (like ingredients in a meal)"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True, help_text='Free-form notes about this exercise')
    details = models.JSONField(default=dict, blank=True, help_text='Exercise-specific data according to activity type schema')
    order = models.IntegerField(default=0, help_text='Order of exercises in the activity')
    
    class Meta:
        db_table = 'activities_activity_exercise'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.exercise.name} in {self.activity}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'exercise': self.exercise.to_dict(),
            'notes': self.notes,
            'details': self.details,
            'order': self.order,
        }
    
    def get_duration_minutes(self) -> Optional[int]:
        """Get duration from details if available"""
        return self.details.get('duration_minutes')
    
    def get_sets(self) -> Optional[int]:
        """Get sets from details if available"""
        return self.details.get('sets')
    
    def get_reps(self) -> Optional[int]:
        """Get reps from details if available"""
        return self.details.get('reps')
    
    def get_weight_kg(self) -> Optional[float]:
        """Get weight from details if available"""
        return self.details.get('weight_kg') or self.details.get('weight')
    
    def get_distance_km(self) -> Optional[float]:
        """Get distance from details if available"""
        return self.details.get('distance_km') or self.details.get('distance')


class ActivityRecord(models.Model):
    """Logged/actual activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_records')
    
    # For planned activities (linked to existing activity)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    
    # For unplanned activities (direct data)
    activity_name = models.CharField(max_length=255, null=True, blank=True)
    activity_type_name = models.CharField(max_length=100, null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)
    
    # Common fields
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_activity_record'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        if self.activity:
            return f"{self.activity.name or self.activity.activity_type.display_name} - {self.date}"
        else:
            return f"{self.activity_name} - {self.date}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'activity': self.activity.to_dict() if self.activity else None,
            'activity_name': self.activity_name,
            'activity_type_name': self.activity_type_name,
            'duration_hours': self.duration_hours,
            'date': self.date.isoformat(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def get_activity_type(self):
        """Get the activity type for this record"""
        if self.activity:
            return self.activity.activity_type
        elif self.activity_type_name:
            try:
                return ActivityType.objects.get(name=self.activity_type_name)
            except ActivityType.DoesNotExist:
                return None
        return None
    
    def get_duration_hours(self):
        """Get duration for this activity record"""
        if self.activity:
            return self.activity.duration_hours
        else:
            return self.duration_hours or 0
    
    def get_calories_burned(self) -> Optional[float]:
        """Calculate calories burned for this activity record"""
        activity_type = self.get_activity_type()
        if not activity_type or not activity_type.calories_per_hour_per_kg:
            return None
        
        # Get user weight (you might want to get this from user profile)
        # For now, using a default weight of 70kg
        user_weight_kg = 70.0
        
        # Calculate calories: calories_per_hour_per_kg * weight * duration_hours
        duration = self.get_duration_hours()
        calories = activity_type.calories_per_hour_per_kg * user_weight_kg * duration
        return round(calories, 1)
