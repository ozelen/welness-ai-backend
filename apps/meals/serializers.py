from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Diet, Meal, Category, Ingredient, MealIngredient, 
    MealRecord, MealPreference
)
from goals.models import Goal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'goal_type', 'notes', 'target_date', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']


class IngredientSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'category', 'category_id', 'proteins', 'fats', 
            'carbs', 'calories', 'fibers', 'sugars', 'description',
            'created_at', 'updated_at'
        ]


class DietSerializer(serializers.ModelSerializer):
    goal = GoalSerializer(read_only=True)
    goal_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Diet
        fields = [
            'id', 'name', 'user', 'goal', 'goal_id', 'day_proteins_g',
            'day_fats_g', 'day_carbohydrates_g', 'day_calories_kcal',
            'is_active', 'start_date', 'end_date', 'notes', 'created_at', 'updated_at'
        ]


class MealIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MealIngredient
        fields = [
            'id', 'meal', 'ingredient', 'ingredient_id', 'barcode',
            'quantity', 'unit', 'created_at', 'updated_at'
        ]


class MealSerializer(serializers.ModelSerializer):
    diet = DietSerializer(read_only=True)
    diet_id = serializers.IntegerField(write_only=True)
    ingredients = MealIngredientSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meal
        fields = [
            'id', 'name', 'description', 'diet', 'diet_id',
            'ingredients', 'is_scheduled', 'start_date', 'start_time', 'duration_minutes',
            'recurrence_type', 'recurrence_until', 'meal_type', 'created_at', 'updated_at'
        ]


class MealEditSerializer(serializers.ModelSerializer):
    """Simplified serializer for meal editing without nested Goal serialization"""
    diet_id = serializers.IntegerField(source='diet.id', read_only=True)
    
    class Meta:
        model = Meal
        fields = [
            'id', 'name', 'description', 'diet_id',
            'created_at', 'updated_at'
        ]


class MealRecordSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    meal_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MealRecord
        fields = [
            'id', 'meal', 'meal_id', 'timestamp', 'photo', 'user',
            'feedback', 'created_at', 'updated_at'
        ]


class MealPreferenceSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MealPreference
        fields = [
            'id', 'user', 'ingredient', 'ingredient_id', 'barcode',
            'description', 'preference_type', 'created_at', 'updated_at'
        ]


class MealPreferenceCreateSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.IntegerField(write_only=True)
    ingredient_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = MealPreference
        fields = [
            'ingredient_id', 'ingredient_name', 'barcode',
            'description', 'preference_type'
        ]


class MealPreferenceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPreference
        fields = ['description', 'preference_type']


class IngredientSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'category', 'calories', 'proteins', 'fats', 'carbs'] 