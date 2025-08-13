from django.urls import path
from . import views

app_name = 'meals'

urlpatterns = [
    # Web page views
    path('', views.meals_dashboard, name='dashboard'),
    path('preferences/', views.preferences_page, name='preferences-page'),
    path('ingredients/', views.ingredients_page, name='ingredients-page'),
    
    # Diet endpoints
    path('diets/', views.DietListView.as_view(), name='diet-list'),
    path('diets/<int:pk>/', views.DietDetailView.as_view(), name='diet-detail'),
    
    # Meal endpoints
    path('meals/', views.MealListView.as_view(), name='meal-list'),
    path('meals/<int:pk>/', views.MealDetailView.as_view(), name='meal-detail'),
    
    # Category endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Ingredient endpoints
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
    
    # Meal preference endpoints (main focus)
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
    path('ingredients/<int:ingredient_id>/update/', views.update_ingredient, name='update-ingredient'),
    path('ingredients/<int:ingredient_id>/get/', views.get_ingredient, name='get-ingredient'),
]
