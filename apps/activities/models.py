from django.db import models
from django.contrib.auth.models import User
from typing import Dict, Any


class ActivityType(models.Model):
    """Activity types with their energy expenditure rates from deficits.csv"""
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    calories_per_hour_per_kg = models.FloatField(help_text='Calories burned per hour per kg of body weight')
    category = models.CharField(max_length=50, blank=True, help_text='Category like "Cardio", "Strength", "Work"')
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text='Pre-defined activity types that come with the system')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text='User who created this activity type (null for system defaults)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_activity_type'
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return self.display_name
    
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
        }


class Activity(models.Model):
    """Planned activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planned_activities')
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE)
    duration_hours = models.FloatField(help_text='Planned duration in hours')
    date = models.DateField()
    is_completed = models.BooleanField(default=False, help_text='Whether this planned activity was completed')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activities_activity'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.user.username} - {self.activity_type.display_name} ({self.duration_hours}h) on {self.date}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'activity_type': self.activity_type.to_dict(),
            'duration_hours': self.duration_hours,
            'date': self.date.isoformat(),
            'is_completed': self.is_completed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class ActivityRecord(models.Model):
    """Logged/actual activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_records')
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE)
    duration_hours = models.FloatField(help_text='Actual duration in hours')
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activities_activity_record'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type.display_name} ({self.duration_hours}h) on {self.date}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'activity_type': self.activity_type.to_dict(),
            'duration_hours': self.duration_hours,
            'date': self.date.isoformat(),
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }
