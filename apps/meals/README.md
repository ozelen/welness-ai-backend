# Meals App

A comprehensive meal management system with nutritional tracking, diet planning, and Google Calendar integration.

## Features

### Core Meal Management
- **Meal Creation & Editing**: Create and edit meals with descriptions
- **Ingredient Management**: Add ingredients to meals with specific quantities (in grams)
- **Nutritional Tracking**: Automatic calculation of calories, proteins, carbs, and fats
- **Diet Association**: Link meals to specific diets and goals

### Diet Management
- **Active Diet System**: Only one diet can be active per user at a time
- **Diet Timeline**: Track diet start/end dates and notes
- **Goal Integration**: Connect diets to fitness goals (weight loss, muscle gain, etc.)
- **Diet Filtering**: Filter meals by diet on the management page

### Meal Scheduling & Calendar Integration
- **Quick Scheduling**: One-click meal scheduling with default settings
- **Google Calendar Ready**: Automatic event creation with proper formatting
- **Recurrence Support**: Daily and weekly recurring meals
- **Meal Types**: Different meal categories (regular, cheat, refeed, pre/post-workout, snack)
- **Visual Indicators**: Clear UI showing scheduled vs unscheduled meals

### Preference System
- **Emoji-based Preferences**: Quick preference selection with emojis (❤️, 👍, 👎, 😡, 🚫, ⚠️)
- **Ingredient Preferences**: Track user preferences for ingredients
- **Quick Actions**: Add, update, or remove preferences with single clicks

## Models

### Diet
- `name`, `user`, `goal` - Basic diet information
- `day_proteins_g`, `day_fats_g`, `day_carbohydrates_g`, `day_calories_kcal` - Daily targets
- `is_active` - Only one diet active per user
- `start_date`, `end_date`, `notes` - Diet timeline tracking

### Meal
- `name`, `description`, `diet` - Basic meal information
- `is_scheduled`, `start_date`, `start_time`, `duration_minutes` - Scheduling
- `recurrence_type`, `recurrence_until` - Recurrence settings
- `meal_type` - Meal category (regular, cheat, refeed, etc.)
- `google_calendar_event_id`, `last_synced_to_calendar` - Calendar integration

### Ingredient
- `name`, `category` - Basic ingredient information
- `calories`, `proteins`, `carbohydrates`, `fats` - Nutritional values (per 100g)

### MealIngredient
- `meal`, `ingredient`, `quantity` - Links meals to ingredients with quantities

### MealPreference
- `user`, `ingredient`, `preference_type` - User preferences for ingredients

## API Endpoints

### Meal Management
- `GET /meals/meals/` - List meals
- `POST /meals/meals/` - Create meal
- `GET /meals/meals/{id}/` - Get meal details
- `PUT /meals/meals/{id}/` - Update meal
- `DELETE /meals/meals/{id}/` - Delete meal

### Meal Scheduling
- `POST /meals/meals/{id}/schedule/` - Schedule meal
- `DELETE /meals/meals/{id}/unschedule/` - Unschedule meal

### Ingredient Management
- `GET /meals/ingredients/` - List ingredients
- `POST /meals/ingredients/` - Create ingredient
- `PUT /meals/ingredients/{id}/` - Update ingredient
- `GET /meals/ingredients/{id}/` - Get ingredient details

### Meal Ingredients
- `POST /meals/meals/{id}/ingredients/` - Add ingredient to meal
- `PUT /meals/meals/{id}/ingredients/{ingredient_id}/` - Update meal ingredient quantity
- `DELETE /meals/meals/{id}/ingredients/{ingredient_id}/` - Remove ingredient from meal

### Preferences
- `POST /meals/preferences/` - Create/update preference
- `DELETE /meals/preferences/{id}/` - Delete preference

### Diet Management
- `POST /meals/diets/{id}/set-active/` - Set active diet

## Calendar Integration

### Google Calendar Service
The app includes a `GoogleCalendarService` class that handles:
- Event creation with proper Google Calendar formatting
- Recurrence rule generation (RRULE)
- Color coding based on meal types
- Bi-directional sync preparation

### Event Format
- **Summary**: "Meal: {meal_name}"
- **Description**: Includes diet name, meal type, and calories
- **Duration**: Configurable (default 30 minutes)
- **Colors**: Different colors for different meal types
- **Recurrence**: Daily/weekly patterns with end dates

### Future Enhancements
- Google OAuth integration
- Bi-directional sync (calendar → app)
- Advanced scheduling UI
- Multiple calendar support

## Usage

### Quick Meal Scheduling
1. Navigate to the meals management page
2. Click the clock icon on any meal
3. Meal is automatically scheduled for today at 12:00 PM
4. Green calendar icon appears to indicate scheduled status

### Managing Preferences
1. Go to the ingredients page
2. Click emoji buttons to set preferences
3. Use the X button to remove preferences
4. Click "Details" for advanced preference options

### Diet Management
1. Use the diet filter dropdown to view meals by diet
2. Active diet is highlighted with "(Active)" label
3. Click "Change Active Diet" to switch active diets
4. Only one diet can be active at a time

## Development

### Running the App
```bash
# Using the Makefile
make run

# Or manually
cd apps
uv run manage.py runserver
```

### Database Migrations
```bash
make makemigrations
make migrate
```

### Creating Test Data
```bash
# Set initial active diet for existing users
uv run manage.py set_initial_active_diet
```

## Templates

### Main Templates
- `dashboard.html` - Main meals dashboard with stats
- `meals.html` - Meal management page with CRUD operations
- `ingredients.html` - Ingredient management with preferences
- `preferences.html` - Preference management page

### Key Features
- Responsive design with Tailwind CSS
- Real-time updates with JavaScript
- Modal-based forms for better UX
- Visual indicators for scheduled meals and active diets 