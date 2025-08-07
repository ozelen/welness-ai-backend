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