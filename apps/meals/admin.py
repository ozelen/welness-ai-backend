from django.contrib import admin
from .models import Meal, Ingredient, MealIngredient, MealRecord, MealPreference

# Register your models here.
admin.site.register(Meal)
admin.site.register(MealIngredient)
admin.site.register(Ingredient)
admin.site.register(MealRecord)
admin.site.register(MealPreference)
