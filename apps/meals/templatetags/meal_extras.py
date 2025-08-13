from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def get_preference_display(preference_type):
    """Get display name for preference type"""
    preference_types = {
        'love': 'Love',
        'like': 'Like', 
        'dislike': 'Dislike',
        'hate': 'Hate',
        'restriction': 'Restriction',
        'allergy': 'Allergy'
    }
    return preference_types.get(preference_type, preference_type)


@register.filter
def calculate_total_calories(meal):
    """Calculate total calories for a meal"""
    total = 0
    for meal_ingredient in meal.mealingredient_set.all():
        # Calculate based on quantity (assuming nutritional values are per 100g)
        ratio = meal_ingredient.quantity / 100
        total += meal_ingredient.ingredient.calories * ratio
    return total


@register.filter
def calculate_total_proteins(meal):
    """Calculate total proteins for a meal"""
    total = 0
    for meal_ingredient in meal.mealingredient_set.all():
        ratio = meal_ingredient.quantity / 100
        total += meal_ingredient.ingredient.proteins * ratio
    return total


@register.filter
def calculate_total_carbs(meal):
    """Calculate total carbohydrates for a meal"""
    total = 0
    for meal_ingredient in meal.mealingredient_set.all():
        ratio = meal_ingredient.quantity / 100
        total += meal_ingredient.ingredient.carbs * ratio
    return total


@register.filter
def calculate_total_fats(meal):
    """Calculate total fats for a meal"""
    total = 0
    for meal_ingredient in meal.mealingredient_set.all():
        ratio = meal_ingredient.quantity / 100
        total += meal_ingredient.ingredient.fats * ratio
    return total 