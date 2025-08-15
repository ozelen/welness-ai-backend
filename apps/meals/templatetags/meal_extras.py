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

@register.filter
def format_recurrence(recurrence_type):
    """Format recurrence type for display"""
    recurrence_map = {
        'daily': 'Daily',
        'weekly': 'Weekly', 
        'weekday': 'Weekdays',
        'weekend': 'Weekends',
        'custom': 'Custom',
        'none': ''
    }
    return recurrence_map.get(recurrence_type, recurrence_type)


@register.filter
def in_set(value, set_obj):
    """Check if value is in set"""
    return value in set_obj


@register.filter
def get_battery_icon(taken, planned):
    """Get battery icon based on taken vs planned percentage"""
    if planned <= 0:
        return 'empty'
    
    percentage = (taken / planned) * 100
    
    if percentage >= 90:
        return 'full'  # Green full battery
    elif percentage >= 50:
        return 'half'  # Yellow half battery
    else:
        return 'low'   # Red low battery


@register.filter
def get_battery_color(taken, planned):
    """Get battery color based on taken vs planned percentage"""
    if planned <= 0:
        return 'text-gray-400'
    
    percentage = (taken / planned) * 100
    
    if percentage >= 90:
        return 'text-green-600'  # Green for good adherence
    elif percentage >= 50:
        return 'text-yellow-600'  # Yellow for moderate adherence
    else:
        return 'text-red-600'     # Red for low adherence


@register.filter
def get_overtaken_icon(taken, planned):
    """Get attention icon if taken is more than 10% over planned"""
    if planned <= 0:
        return None
    
    percentage = (taken / planned) * 100
    
    if percentage > 110:  # More than 10% over
        return 'attention'
    return None


@register.filter
def div(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 