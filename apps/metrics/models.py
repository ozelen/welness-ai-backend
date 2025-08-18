from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from typing import Optional, Dict, Any, List
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
import math


class Metric(models.Model):
    """Unified model for all types of health metrics"""
    METRIC_TYPES = [
        ('body_measurement', 'Body Measurement'),
        ('lab_result', 'Laboratory Result'),
        ('vital_sign', 'Vital Sign'),
        ('fitness', 'Fitness Metric'),
        ('nutrition', 'Nutrition Metric'),
        ('calculated', 'Calculated Metric'),  # Added for LBM, BMR, TDEE, etc.
        ('custom', 'Custom Metric'),
    ]
    
    # Unique alphanumeric ID for formulas
    metric_id = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="Unique alphanumeric ID for use in formulas (e.g., 'WEIGHT', 'HEIGHT', 'BF_PCT')")
    
    # Basic metric information
    name = models.CharField(max_length=255, unique=True, help_text="Unique name for the metric (e.g., 'Weight', 'Blood Glucose')")
    type = models.CharField(max_length=20, choices=METRIC_TYPES, help_text="Category of the metric")
    unit = models.CharField(max_length=50, help_text="Unit of measurement (e.g., kg, cm, mg/dL, pmol/L)")
    description = models.TextField(blank=True, help_text="Description of what this metric measures")
    
    # Customization options
    is_custom = models.BooleanField(default=False, help_text="Whether this is a user-created custom metric")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                                 help_text="User who created this custom metric")
    is_public = models.BooleanField(default=True, help_text="Whether this metric is available to all users")
    
    # Validation and display
    min_value = models.FloatField(null=True, blank=True, help_text="Minimum acceptable value")
    max_value = models.FloatField(null=True, blank=True, help_text="Maximum acceptable value")
    reference_range = models.CharField(max_length=100, blank=True, help_text="Normal range (e.g., 70-100)")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or identifier")
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    
    # For calculated metrics
    is_calculated = models.BooleanField(default=False, help_text="Whether this metric is calculated from other metrics")
    calculation_formula = models.TextField(blank=True, help_text="Formula or description of how this metric is calculated")
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship for user favorites
    favorited_by = models.ManyToManyField(User, through='UserMetricFavorite', related_name='favorite_metrics')

    class Meta:
        ordering = ['type', 'name']
        indexes = [
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['is_custom', 'created_by']),
            models.Index(fields=['is_calculated']),
        ]

    def __str__(self):
        return f"{self.name} ({self.unit})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'metric_id': self.metric_id,
            'name': self.name,
            'type': self.type,
            'type_display': self.get_type_display(),
            'unit': self.unit,
            'description': self.description,
            'is_custom': self.is_custom,
            'is_calculated': self.is_calculated,
            'calculation_formula': self.calculation_formula,
            'created_by_id': self.created_by.id if self.created_by else None,
            'is_public': self.is_public,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'reference_range': self.reference_range,
            'icon': self.icon,
            'color': self.color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
        }


class MetricValue(models.Model):
    """Values for metrics - replaces BodyMeasurement, LabResult, etc."""
    MEASUREMENT_TYPES = [
        ('baseline', 'Baseline'),
        ('target', 'Target'),
        ('current', 'Current'),  # Added for current values
        ('log', 'Log'),
        ('goal', 'Goal'),
        ('calculated', 'Calculated'),  # Added for calculated metrics
    ]
    
    RESULT_STATUS = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('low', 'Low'),
        ('critical', 'Critical'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metric_values')
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='values')
    
    # Value and metadata
    value = models.FloatField(help_text="The measured value")
    measurement_type = models.CharField(max_length=20, choices=MEASUREMENT_TYPES, default='log')
    status = models.CharField(max_length=20, choices=RESULT_STATUS, default='normal')
    
    # Additional context
    notes = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True, help_text="Source of measurement (e.g., 'Home Scale', 'Lab Corp')")
    
    # For calculated metrics - store the input values used for calculation
    calculation_inputs = models.JSONField(blank=True, null=True, help_text="Input values used for calculation")
    
    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'metric', 'timestamp']),
            models.Index(fields=['metric', 'timestamp']),
            models.Index(fields=['measurement_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.metric.name}: {self.value} {self.metric.unit}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'user_id': self.user.id,
            'metric': self.metric.to_dict(),
            'value': self.value,
            'measurement_type': self.measurement_type,
            'measurement_type_display': self.get_measurement_type_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'notes': self.notes,
            'source': self.source,
            'calculation_inputs': self.calculation_inputs,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat(),
        }


class HealthCalculator(models.Model):
    """Health calculations session - stores input data and triggers metric calculations"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('lightly_active', 'Lightly Active (light exercise 1-3 days/week)'),
        ('moderately_active', 'Moderately Active (moderate exercise 3-5 days/week)'),
        ('very_active', 'Very Active (hard exercise 6-7 days/week)'),
        ('extremely_active', 'Extremely Active (very hard exercise, physical job)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics_healthcalculators')
    
    # Input data (can be auto-populated from latest measurements)
    weight_kg = models.FloatField(help_text="Body weight in kilograms")
    height_cm = models.FloatField(help_text="Height in centimeters")
    body_fat_percentage = models.FloatField(help_text="Body fat percentage")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default='moderately_active')
    
    # Activity tracking
    activity_hours_per_week = models.FloatField(default=0, help_text="Total hours of exercise per week")
    
    # Metadata
    calculation_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-calculation_date']
        indexes = [
            models.Index(fields=['user', 'calculation_date']),
        ]

    def __str__(self):
        return f"{self.user.username}'s health calculator - {self.calculation_date.strftime('%Y-%m-%d')}"
    
    def get_age(self) -> Optional[int]:
        """Calculate age from user's date of birth"""
        try:
            # Check if user has a profile
            if not hasattr(self.user, 'profile'):
                print(f"User {self.user.username} has no profile")
                return None
            
            # Check if profile has date of birth
            if not self.user.profile.date_of_birth:
                print(f"User {self.user.username} has no date of birth set")
                return None
            
            # Calculate age
            today = date.today()
            age = today.year - self.user.profile.date_of_birth.year - (
                (today.month, today.day) < (self.user.profile.date_of_birth.month, self.user.profile.date_of_birth.day)
            )
            
            # Validate age is reasonable
            if age < 0 or age > 120:
                print(f"User {self.user.username} has invalid age: {age}")
                return None
            
            print(f"User {self.user.username} age calculated: {age}")
            return age
            
        except Exception as e:
            print(f"Error calculating age for user {self.user.username}: {e}")
            return None
    
    def calculate_and_store_metrics(self) -> Dict[str, Any]:
        """
        Calculate all health metrics and store them as MetricValue instances
        Returns a dictionary with the calculated values
        """
        from .services import HealthCalculatorService
        
        results = {}
        calculation_inputs = {
            'weight_kg': self.weight_kg,
            'height_cm': self.height_cm,
            'body_fat_percentage': self.body_fat_percentage,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'age': self.get_age(),
        }
        
        # Calculate and store LBM
        lbm_kg = HealthCalculatorService.calculate_lbm(self.weight_kg, self.body_fat_percentage)
        if lbm_kg:
            self._store_calculated_metric('Lean Body Mass', lbm_kg, calculation_inputs)
            results['lbm_kg'] = lbm_kg
        
        # Calculate and store BMI
        bmi = HealthCalculatorService.calculate_bmi(self.weight_kg, self.height_cm)
        self._store_calculated_metric('BMI', bmi, calculation_inputs)
        results['bmi'] = bmi
        
        # Calculate and store Body Fat Mass
        body_fat_mass_kg = HealthCalculatorService.calculate_body_fat_mass(self.weight_kg, self.body_fat_percentage)
        self._store_calculated_metric('Body Fat Mass', body_fat_mass_kg, calculation_inputs)
        results['body_fat_mass_kg'] = body_fat_mass_kg
        
        # Calculate and store BMR (requires age)
        age = self.get_age()
        if age:
            bmr_kcal = HealthCalculatorService.calculate_bmr(self.weight_kg, self.height_cm, age, self.gender)
            self._store_calculated_metric('Basal Metabolic Rate', bmr_kcal, calculation_inputs)
            results['bmr_kcal'] = bmr_kcal
            
            # Calculate and store TDEE
            tdee_kcal = HealthCalculatorService.calculate_tdee(bmr_kcal, self.activity_level)
            self._store_calculated_metric('Total Daily Energy Expenditure', tdee_kcal, calculation_inputs)
            results['tdee_kcal'] = tdee_kcal
        else:
            # Use default age of 30 if no age is provided (common average)
            default_age = 30
            bmr_kcal = HealthCalculatorService.calculate_bmr(self.weight_kg, self.height_cm, default_age, self.gender)
            self._store_calculated_metric('Basal Metabolic Rate', bmr_kcal, calculation_inputs)
            results['bmr_kcal'] = bmr_kcal
            
            # Calculate and store TDEE
            tdee_kcal = HealthCalculatorService.calculate_tdee(bmr_kcal, self.activity_level)
            self._store_calculated_metric('Total Daily Energy Expenditure', tdee_kcal, calculation_inputs)
            results['tdee_kcal'] = tdee_kcal
            
            # Add note about default age
            calculation_inputs['note'] = f"BMR calculated using default age of {default_age} years. Please update your date of birth in your profile for more accurate results."
        
        return results
    
    def _store_calculated_metric(self, metric_name: str, value: float, calculation_inputs: Dict[str, Any]):
        """Store a calculated metric as a MetricValue"""
        try:
            metric = Metric.objects.get(name=metric_name, is_active=True)
            MetricValue.objects.create(
                user=self.user,
                metric=metric,
                value=value,
                measurement_type='calculated',
                status='normal',
                notes=f"Calculated from health calculator session {self.id}",
                source='Health Calculator',
                calculation_inputs=calculation_inputs,
                timestamp=self.calculation_date
            )
        except Metric.DoesNotExist:
            # If metric doesn't exist, create it
            unit_map = {
                'Lean Body Mass': 'kg',
                'BMI': '',
                'Body Fat Mass': 'kg',
                'Basal Metabolic Rate': 'kcal/day',
                'Total Daily Energy Expenditure': 'kcal/day',
            }
            
            metric = Metric.objects.create(
                name=metric_name,
                type='calculated',
                unit=unit_map.get(metric_name, ''),
                description=f"Calculated {metric_name.lower()}",
                is_calculated=True,
                is_public=True,
                icon='fas fa-calculator',
                color='#667eea'
            )
            
            MetricValue.objects.create(
                user=self.user,
                metric=metric,
                value=value,
                measurement_type='calculated',
                status='normal',
                notes=f"Calculated from health calculator session {self.id}",
                source='Health Calculator',
                calculation_inputs=calculation_inputs,
                timestamp=self.calculation_date
            )
    
    def get_calculated_results(self) -> Dict[str, Any]:
        """Get the calculated results from stored MetricValue instances"""
        results = {}
        
        # Get calculated metrics for this session
        calculated_values = MetricValue.objects.filter(
            user=self.user,
            measurement_type='calculated',
            timestamp=self.calculation_date
        ).select_related('metric')
        
        for value in calculated_values:
            metric_name = value.metric.name
            if metric_name == 'Lean Body Mass':
                results['lbm_kg'] = value.value
            elif metric_name == 'BMI':
                results['bmi'] = value.value
            elif metric_name == 'Body Fat Mass':
                results['body_fat_mass_kg'] = value.value
            elif metric_name == 'Basal Metabolic Rate':
                results['bmr_kcal'] = value.value
            elif metric_name == 'Total Daily Energy Expenditure':
                results['tdee_kcal'] = value.value
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for API responses
        """
        calculated_results = self.get_calculated_results()
        
        return {
            'id': str(self.id),
            'user_id': self.user.id,
            'weight_kg': self.weight_kg,
            'height_cm': self.height_cm,
            'body_fat_percentage': self.body_fat_percentage,
            'gender': self.gender,
            'gender_display': self.get_gender_display(),
            'activity_level': self.activity_level,
            'activity_level_display': self.get_activity_level_display(),
            'activity_hours_per_week': self.activity_hours_per_week,
            'age': self.get_age(),
            'calculation_date': self.calculation_date.isoformat(),
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            # Include calculated results
            'lbm_kg': calculated_results.get('lbm_kg'),
            'bmr_kcal': calculated_results.get('bmr_kcal'),
            'tdee_kcal': calculated_results.get('tdee_kcal'),
            'bmi': calculated_results.get('bmi'),
            'body_fat_mass_kg': calculated_results.get('body_fat_mass_kg'),
        }





class UserMetricFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'metric']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.metric.name}"
