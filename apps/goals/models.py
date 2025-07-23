from django.db import models
from django.contrib.auth.models import User
from datetime import date
from typing import Optional
import uuid


class Goal(models.Model):
    GOAL_TYPES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
        ('general_fitness', 'General Fitness'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES)
    target_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True) # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.get_goal_type_display()} goal"  # type: ignore
    
    def to_dict(self) -> dict:
        """Convert goal to dictionary for API responses"""
        return {
            'id': str(self.id),
            'goal_type': self.goal_type,
            'goal_type_display': self.get_goal_type_display(),  # type: ignore
            'target_date': self.target_date.isoformat() if self.target_date else None,  # type: ignore
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),  # type: ignore
            'updated_at': self.updated_at.isoformat(),  # type: ignore
            'days_remaining': (self.target_date - date.today()).days if self.target_date else None
        }
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until target date"""
        if self.target_date:
            return (self.target_date - date.today()).days
        return None

class BodyMeasurement(models.Model):
    BODY_METRICS = [
        ('weight_kg', 'Weight (kg)'),
        ('waist_cm', 'Waist (cm)'),
        ('hip_cm', 'Hip (cm)'),
        ('neck_cm', 'Neck (cm)'),
        ('arm_circumference_cm', 'Arm Circumference (cm)'),
        ('thigh_circumference_cm', 'Thigh Circumference (cm)'),
        ('calf_circumference_cm', 'Calf Circumference (cm)'),
        ('body_fat_percentage', 'Body Fat (%)'),
        ('muscle_mass_percentage', 'Muscle Mass (%)'),
        ('bmi_value', 'BMI Value'),
    ]
    MEASUREMENT_TYPES = [
        ('target', 'Target'),
        ('baseline', 'Baseline'),
        ('log', 'Log'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)
    metric = models.CharField(max_length=50, choices=BODY_METRICS, default='weight_kg')
    measurement_type = models.CharField(max_length=50, choices=MEASUREMENT_TYPES)
    value = models.FloatField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.goal.user.username}'s {self.get_measurement_type_display()} {self.get_metric_display()} measurement"
    
    def to_dict(self) -> dict:
        """Convert body measurement to dictionary for API responses"""
        return {
            'id': self.id, # type: ignore
            'goal_id': str(self.goal.id) if self.goal else None,
            'metric': self.metric,
            'metric_display': self.get_metric_display(), # type: ignore
            'measurement_type': self.measurement_type,
            'measurement_type_display': self.get_measurement_type_display(), # type: ignore
            'value': self.value,
            'timestamp': self.timestamp.isoformat(), # type: ignore
            'created_at': self.created_at.isoformat() # type: ignore
        }
