from django.urls import path
from . import views

app_name = 'meals'

urlpatterns = [
    # Web page views
    path('', views.meals_dashboard, name='dashboard'),
    path('preferences-page/', views.preferences_page, name='preferences-page'),
    path('ingredients-page/', views.ingredients_page, name='ingredients-page'),
    path('manage/', views.meals_management_page, name='meals'),
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Diet endpoints
    path('diets/', views.DietListView.as_view(), name='diet-list'),
    path('diets/<int:pk>/', views.DietDetailView.as_view(), name='diet-detail'),
    
    # Meal endpoints (API)
    path('meals/', views.MealListView.as_view(), name='meal-list'),
    path('meals/<int:pk>/', views.MealDetailView.as_view(), name='meal-detail'),
    
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Ingredient endpoints (API)
    path('ingredients/', views.IngredientListView.as_view(), name='ingredient-list'),
    path('ingredients/<int:pk>/', views.IngredientDetailView.as_view(), name='ingredient-detail'),
    path('ingredients/search/', views.IngredientSearchView.as_view(), name='ingredient-search'),
    path('ingredients/suggestions/', views.ingredient_suggestions, name='ingredient-suggestions'),
    
    # Meal ingredient endpoints
    path('meals/<int:meal_id>/ingredients/', views.MealIngredientListView.as_view(), name='meal-ingredient-list'),
    path('meal-ingredients/<int:pk>/', views.MealIngredientDetailView.as_view(), name='meal-ingredient-detail'),
    
    # Meal record endpoints
    path('meal-records/', views.MealRecordListView.as_view(), name='meal-record-list'),
    path('meal-records/<int:pk>/', views.MealRecordDetailView.as_view(), name='meal-record-detail'),
    
    # Meal preference endpoints (API)
    path('preferences/', views.MealPreferenceListView.as_view(), name='meal-preference-list'),
    path('preferences/<int:pk>/', views.MealPreferenceDetailView.as_view(), name='meal-preference-detail'),
    path('preferences/type/<str:preference_type>/', views.MealPreferenceByTypeView.as_view(), name='meal-preference-by-type'),
    path('preferences/summary/', views.user_meal_preferences_summary, name='meal-preference-summary'),
    path('preferences/bulk-update/', views.bulk_update_meal_preferences, name='bulk-update-preferences'),
    path('preferences/<int:preference_id>/delete/', views.delete_meal_preference, name='delete-meal-preference'),
    
    # Quick preference endpoints
    path('preferences/quick-update/', views.quick_preference_update, name='quick-preference-update'),
    path('preferences/quick-delete/<int:ingredient_id>/', views.quick_preference_delete, name='quick-preference-delete'),
    
    # Ingredient CRUD endpoints
    path('ingredients/create/', views.create_ingredient, name='create-ingredient'),
    path('ingredients/create-from-form/', views.create_ingredient_from_form, name='create-ingredient-from-form'),
    path('ingredients/<int:ingredient_id>/update/', views.update_ingredient, name='update-ingredient'),
    path('ingredients/<int:ingredient_id>/get/', views.get_ingredient, name='get-ingredient'),
    
    # Meals management endpoints
    path('meals/create/', views.create_meal, name='create-meal'),
    path('meals/<int:meal_id>/update/', views.update_meal, name='update-meal'),
    path('meals/<int:meal_id>/get/', views.get_meal, name='get-meal'),
    path('meals/<int:meal_id>/delete/', views.delete_meal, name='delete-meal'),
    path('meals/<int:meal_id>/add-ingredient/', views.add_ingredient_to_meal, name='add-ingredient-to-meal'),
    path('meal-ingredients/<int:meal_ingredient_id>/update/', views.update_meal_ingredient, name='update-meal-ingredient'),
    path('meal-ingredients/<int:meal_ingredient_id>/remove/', views.remove_ingredient_from_meal, name='remove-ingredient-from-meal'),
    
    # Diet management endpoints
    path('diets/<int:diet_id>/set-active/', views.set_active_diet, name='set-active-diet'),
    
    # Meal scheduling endpoints
    path('meals/<int:meal_id>/schedule/', views.schedule_meal, name='schedule-meal'),
    path('meals/<int:meal_id>/unschedule/', views.unschedule_meal, name='unschedule-meal'),
    
    # Meal completion endpoints
    path('meals/<int:meal_id>/complete/', views.mark_meal_completed, name='mark-meal-completed'),
    path('meals/<int:meal_id>/uncomplete/', views.unmark_meal_completed, name='unmark-meal-completed'),
    path('meals/<int:meal_id>/completion-status/', views.get_meal_completion_status, name='get-meal-completion-status'),
    
    # Meal feedback endpoints
    path('meals/<int:meal_id>/feedback/', views.MealFeedbackView.as_view(), name='meal-feedback'),
    
    # Create and schedule meal from calendar
    path('meals/create-and-schedule/', views.create_and_schedule_meal, name='create-and-schedule-meal'),
    
    # Log meal record (no diet/meal creation)
    path('meals/log-meal/', views.log_meal, name='log-meal'),
    
    # Delete meal record
    path('meals/record/<int:record_id>/delete/', views.delete_meal_record, name='delete-meal-record'),
    
    # AI-powered ingredient suggestions and nutrition
    path('ingredients/ai-suggestions/', views.ai_ingredient_suggestions, name='ai-ingredient-suggestions'),
    path('ingredients/ai-nutrition/', views.ai_nutrition_lookup, name='ai-nutrition-lookup'),
]
