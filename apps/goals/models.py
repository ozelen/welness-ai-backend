from django.db import models
from django.contrib.auth.models import User
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.get_goal_type_display()} goal"

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
