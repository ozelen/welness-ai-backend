from django.db import models
from django.contrib.auth.models import User
from goals.models import Goal

class Diet(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    day_proteins_g = models.FloatField()
    day_fats_g = models.FloatField()
    day_carbohydrates_g = models.FloatField()
    day_calories_kcal = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Meal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    diet = models.ForeignKey(Diet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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