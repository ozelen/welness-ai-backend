# Meals App

This Django app provides comprehensive meal management functionality including diets, meals, ingredients, and user meal preferences.

## Models

### Core Models
- **Diet**: User's dietary plans with nutritional targets
- **Meal**: Individual meals within a diet
- **Category**: Ingredient categories (e.g., Vegetables, Fruits, Proteins)
- **Ingredient**: Food items with nutritional information
- **MealIngredient**: Junction table linking meals to ingredients with quantities
- **MealRecord**: User's meal consumption records
- **MealPreference**: User's food preferences and restrictions

### MealPreference Model

The `MealPreference` model is the core feature for managing user food preferences:

```python
PREFERENCE_TYPES = [
    ('love', 'Love'),
    ('like', 'Like'),
    ('dislike', 'Dislike'),
    ('hate', 'Hate'),
    ('restriction', 'Restriction'),
    ('allergy', 'Allergy')
]
```

## API Endpoints

### Meal Preferences (Main Feature)

#### List/Create Preferences
- **GET** `/meals/preferences/` - List user's meal preferences
- **POST** `/meals/preferences/` - Create new meal preference

**POST Data:**
```json
{
    "ingredient_id": 1,
    "preference_type": "love",
    "description": "I love this ingredient!"
}
```

Or create with new ingredient:
```json
{
    "ingredient_name": "New Ingredient",
    "preference_type": "dislike",
    "description": "I don't like this"
}
```

#### Individual Preference Management
- **GET** `/meals/preferences/{id}/` - Get specific preference
- **PUT/PATCH** `/meals/preferences/{id}/` - Update preference
- **DELETE** `/meals/preferences/{id}/delete/` - Delete preference

#### Filtered Views
- **GET** `/meals/preferences/type/{type}/` - Get preferences by type (love, like, dislike, etc.)
- **GET** `/meals/preferences/summary/` - Get preference statistics

**Summary Response:**
```json
{
    "total_preferences": 10,
    "by_type": {
        "love": 3,
        "like": 4,
        "dislike": 2,
        "hate": 1
    },
    "recent_additions": [...]
}
```

#### Bulk Operations
- **POST** `/meals/preferences/bulk-update/` - Update multiple preferences

**Bulk Update Data:**
```json
{
    "preferences": [
        {
            "id": 1,
            "preference_type": "love",
            "description": "Updated description"
        }
    ]
}
```

### Ingredient Management

#### Search and Suggestions
- **GET** `/meals/ingredients/search/?q=apple` - Search ingredients
- **GET** `/meals/ingredients/suggestions/?q=apple` - Get ingredient suggestions (excludes user's existing preferences)

#### CRUD Operations
- **GET** `/meals/ingredients/` - List all ingredients
- **POST** `/meals/ingredients/` - Create new ingredient
- **GET** `/meals/ingredients/{id}/` - Get specific ingredient
- **PUT/PATCH** `/meals/ingredients/{id}/` - Update ingredient
- **DELETE** `/meals/ingredients/{id}/` - Delete ingredient

### Diet and Meal Management

#### Diets
- **GET** `/meals/diets/` - List user's diets
- **POST** `/meals/diets/` - Create new diet
- **GET** `/meals/diets/{id}/` - Get specific diet
- **PUT/PATCH** `/meals/diets/{id}/` - Update diet
- **DELETE** `/meals/diets/{id}/` - Delete diet

#### Meals
- **GET** `/meals/meals/` - List user's meals
- **POST** `/meals/meals/` - Create new meal
- **GET** `/meals/meals/{id}/` - Get specific meal
- **PUT/PATCH** `/meals/meals/{id}/` - Update meal
- **DELETE** `/meals/meals/{id}/` - Delete meal

#### Meal Ingredients
- **GET** `/meals/meals/{meal_id}/ingredients/` - List meal ingredients
- **POST** `/meals/meals/{meal_id}/ingredients/` - Add ingredient to meal
- **GET** `/meals/meal-ingredients/{id}/` - Get specific meal ingredient
- **PUT/PATCH** `/meals/meal-ingredients/{id}/` - Update meal ingredient
- **DELETE** `/meals/meal-ingredients/{id}/` - Remove ingredient from meal

### Meal Records
- **GET** `/meals/meal-records/` - List user's meal records
- **POST** `/meals/meal-records/` - Create meal record
- **GET** `/meals/meal-records/{id}/` - Get specific meal record
- **PUT/PATCH** `/meals/meal-records/{id}/` - Update meal record
- **DELETE** `/meals/meal-records/{id}/` - Delete meal record

## Usage Examples

### Creating a Meal Preference

```python
import requests

# Create a preference for an existing ingredient
response = requests.post('/meals/preferences/', {
    'ingredient_id': 1,
    'preference_type': 'love',
    'description': 'I love carrots!'
})

# Create a preference with a new ingredient
response = requests.post('/meals/preferences/', {
    'ingredient_name': 'Quinoa',
    'preference_type': 'like',
    'description': 'Good protein source'
})
```

### Getting User's Preferences Summary

```python
response = requests.get('/meals/preferences/summary/')
summary = response.json()

print(f"Total preferences: {summary['total_preferences']}")
print(f"Loved foods: {summary['by_type']['love']}")
```

### Searching for Ingredients

```python
# Search for ingredients
response = requests.get('/meals/ingredients/search/?q=apple')
ingredients = response.json()

# Get suggestions (excluding user's existing preferences)
response = requests.get('/meals/ingredients/suggestions/?q=apple')
suggestions = response.json()['suggestions']
```

## Authentication

All endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Admin Interface

The admin interface provides comprehensive management for all models:

- **MealPreference**: Filter by user, preference type, and ingredient
- **Ingredient**: Search by name, filter by category
- **Meal**: Inline editing of meal ingredients
- **Diet**: User-specific diet management

## Testing

Run the tests with:

```bash
python manage.py test meals
```

The test suite covers:
- Model creation and validation
- API endpoint functionality
- Authentication requirements
- CRUD operations for meal preferences
- Bulk operations
- Search and filtering 