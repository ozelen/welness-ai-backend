from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from goals.models import Goal

class Diet(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    day_proteins_g = models.FloatField()
    day_fats_g = models.FloatField()
    day_carbohydrates_g = models.FloatField()
    day_calories_kcal = models.FloatField()
    is_active = models.BooleanField(default=False)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one diet is active per user
        if self.is_active:
            Diet.objects.filter(user=self.user, is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

class Meal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    
    # Calendar scheduling
    is_scheduled = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=30)
    
    # Recurrence options
    RECURRENCE_TYPES = [
        ('none', 'No Recurrence'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('weekday', 'Weekdays (Mon-Fri)'),
        ('weekend', 'Weekends (Sat-Sun)'),
        ('custom', 'Custom'),
    ]
    recurrence_type = models.CharField(max_length=10, choices=RECURRENCE_TYPES, default='none')
    recurrence_until = models.DateField(null=True, blank=True)
    
    # Google Calendar integration
    google_calendar_event_id = models.CharField(max_length=255, blank=True)
    last_synced_to_calendar = models.DateTimeField(null=True, blank=True)
    
    # Meal types
    MEAL_TYPES = [
        ('regular', 'Regular Meal'),
        ('cheat', 'Cheat Meal'),
        ('refeed', 'Refeed Meal'),
        ('pre_workout', 'Pre-Workout'),
        ('post_workout', 'Post-Workout'),
        ('snack', 'Snack'),
    ]
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='regular')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_calendar_color_id(self):
        """Get Google Calendar color ID based on meal type"""
        color_map = {
            'regular': '1',      # Blue
            'cheat': '4',        # Red
            'refeed': '6',       # Orange
            'pre_workout': '2',  # Green
            'post_workout': '3', # Purple
            'snack': '5',        # Yellow
        }
        return color_map.get(self.meal_type, '1')
    
    def generate_rrule(self):
        """Generate Google Calendar recurrence rule"""
        if self.recurrence_type == 'none':
            return None
        
        if self.recurrence_type == 'daily':
            return {'freq': 'DAILY'}
        
        if self.recurrence_type == 'weekly':
            return {'freq': 'WEEKLY'}
        
        return None
    
    def get_total_calories(self):
        """Calculate total calories for this meal"""
        total = 0
        for meal_ingredient in self.mealingredient_set.all():
            # Calculate based on quantity (assuming nutritional values are per 100g)
            ratio = meal_ingredient.quantity / 100
            total += meal_ingredient.ingredient.calories * ratio
        return total

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    proteins = models.FloatField()
    fats = models.FloatField()
    carbs = models.FloatField()
    calories = models.FloatField()
    fibers = models.FloatField()
    sugars = models.FloatField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.FloatField()
    unit = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.meal.name} - {self.ingredient.name}"
    
class MealRecord(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    photo = models.ImageField(upload_to='meal_photos/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.meal.name} - {self.timestamp}"

class MealPreference(models.Model):
    PREFERENCE_TYPES = [
        ('love', 'Love'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('hate', 'Hate'),
        ('restriction', 'Restriction'),
        ('allergy', 'Allergy')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    preference_type = models.CharField(max_length=255, choices=PREFERENCE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.preference_type} {self.ingredient.name}"