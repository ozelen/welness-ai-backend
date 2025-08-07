from django.contrib import admin
from .models import (
    Diet, Meal, Category, Ingredient, MealIngredient, 
    MealRecord, MealPreference
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories', 'proteins', 'fats', 'carbs']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'goal', 'day_calories_kcal', 'created_at']
    list_filter = ['goal', 'created_at']
    search_fields = ['name', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'diet', 'created_at']
    list_filter = ['diet', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MealIngredientInline]
    autocomplete_fields = ['diet']


@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    list_display = ['meal', 'ingredient', 'quantity', 'unit', 'barcode']
    list_filter = ['meal', 'ingredient', 'unit']
    search_fields = ['meal__name', 'ingredient__name', 'barcode']
    ordering = ['meal__name', 'ingredient__name']
    autocomplete_fields = ['meal', 'ingredient']


@admin.register(MealRecord)
class MealRecordAdmin(admin.ModelAdmin):
    list_display = ['meal', 'user', 'timestamp', 'created_at']
    list_filter = ['timestamp', 'created_at', 'user']
    search_fields = ['meal__name', 'user__username', 'feedback']
    ordering = ['-timestamp']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['meal', 'user']


@admin.register(MealPreference)
class MealPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'ingredient', 'preference_type', 'barcode', 'created_at']
    list_filter = ['preference_type', 'created_at', 'user']
    search_fields = ['user__username', 'ingredient__name', 'barcode', 'description']
    ordering = ['user__username', 'ingredient__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user', 'ingredient']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'ingredient')
