from typing import Optional, Dict, Any, List, Tuple
from datetime import date
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Activity, ActivityRecord, ActivityType


class ActivityService:
    """Service for activity-based TDEE calculation using deficits.csv data"""
    
    @staticmethod
    def get_activity_deficit(activity_type):
        """Get calories per hour per kg for an activity type"""
        return activity_type.calories_per_hour_per_kg
    
    @staticmethod
    def calculate_daily_activity_multiplier(user: User, date: date = None, use_planned: bool = False) -> float:
        """
        Calculate daily activity multiplier based on activities
        Args:
            user: User to calculate for
            date: Date to calculate for (defaults to today)
            use_planned: If True, use planned activities; if False, use actual logged activities
        Returns a multiplier that can be applied to BMR to get TDEE
        """
        if date is None:
            date = timezone.now().date()
        
        # Get user's weight in kg (this would need to be imported from metrics app)
        # For now, we'll use a default weight
        weight_kg = 70.0  # Default weight, should be fetched from metrics
        
        # Get activities for the specified date
        if use_planned:
            # Use planned activities
            activities = Activity.objects.filter(user=user, date=date)
        else:
            # Use actual logged activities
            activities = ActivityRecord.objects.filter(user=user, date=date)
        
        if not activities.exists():
            # If no activities logged, assume sedentary work for 8 hours
            return 1.2  # Sedentary multiplier
        
        # Calculate total energy expenditure from activities
        total_activity_calories = 0
        total_hours = 0
        
        for activity in activities:
            deficit = ActivityService.get_activity_deficit(activity.activity_type)
            activity_calories = deficit * weight_kg * activity.duration_hours
            total_activity_calories += activity_calories
            total_hours += activity.duration_hours
        
        # Calculate BMR for the day (24 hours)
        # This would need to be fetched from metrics app
        bmr = 1500  # Default BMR, should be calculated from metrics
        
        # Calculate activity multiplier
        # TDEE = BMR + Activity Calories
        # Activity Multiplier = TDEE / BMR
        daily_bmr = bmr  # BMR is already daily
        tdee = daily_bmr + total_activity_calories
        activity_multiplier = tdee / daily_bmr
        
        return round(activity_multiplier, 2)
    
    @staticmethod
    def get_daily_activity_summary(user: User, date: date = None) -> Dict[str, Any]:
        """
        Get summary of both planned and actual activities for a day
        """
        if date is None:
            date = timezone.now().date()
        
        planned_activities = Activity.objects.filter(user=user, date=date)
        actual_activities = ActivityRecord.objects.filter(user=user, date=date)
        
        # Calculate planned vs actual
        planned_calories = ActivityService._calculate_activities_calories(user, planned_activities)
        actual_calories = ActivityService._calculate_activities_calories(user, actual_activities)
        
        return {
            'date': date,
            'planned_activities': [activity.to_dict() for activity in planned_activities],
            'actual_activities': [activity.to_dict() for activity in actual_activities],
            'planned_calories': planned_calories,
            'actual_calories': actual_calories,
            'planned_multiplier': ActivityService.calculate_daily_activity_multiplier(user, date, use_planned=True),
            'actual_multiplier': ActivityService.calculate_daily_activity_multiplier(user, date, use_planned=False),
        }
    
    @staticmethod
    def _calculate_activities_calories(user: User, activities) -> float:
        """Helper method to calculate total calories from activities"""
        weight_kg = 70.0  # Default weight, should be fetched from metrics
        total_calories = 0
        
        for activity in activities:
            deficit = ActivityService.get_activity_deficit(activity.activity_type)
            activity_calories = deficit * weight_kg * activity.duration_hours
            total_calories += activity_calories
        
        return round(total_calories, 1)
    
    @staticmethod
    def get_activity_choices() -> List[Tuple[str, str]]:
        """Get list of available activities for forms"""
        return [(at.id, at.display_name) for at in ActivityType.objects.filter(is_active=True).order_by('category', 'display_name')]
