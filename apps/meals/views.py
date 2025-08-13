from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import (
    Diet, Meal, Category, Ingredient, MealIngredient, 
    MealRecord, MealPreference
)
from .serializers import (
    DietSerializer, MealSerializer, CategorySerializer, IngredientSerializer,
    MealIngredientSerializer, MealRecordSerializer, MealPreferenceSerializer,
    MealPreferenceCreateSerializer, MealPreferenceUpdateSerializer,
    IngredientSearchSerializer
)


@login_required
def meals_dashboard(request):
    """Main meals dashboard page"""
    user = request.user
    
    # Get user's data
    diets = Diet.objects.filter(user=user)
    preferences = MealPreference.objects.filter(user=user)
    recent_meals = MealRecord.objects.filter(user=user).order_by('-timestamp')[:5]
    meals = Meal.objects.filter(diet__user=user)
    
    # Get preference summary
    preference_summary = {
        'total': preferences.count(),
        'by_type': {}
    }
    
    for pref_type, _ in MealPreference.PREFERENCE_TYPES:
        count = preferences.filter(preference_type=pref_type).count()
        preference_summary['by_type'][pref_type] = count
    
    context = {
        'diets': diets,
        'meals': meals,
        'preferences': preferences[:10],  # Show first 10 preferences
        'recent_meals': recent_meals,
        'preference_summary': preference_summary,
        'preference_types': MealPreference.PREFERENCE_TYPES,
    }
    
    return render(request, 'meals/dashboard.html', context)


@login_required
def preferences_page(request):
    """Meal preferences management page"""
    user = request.user
    preferences = MealPreference.objects.filter(user=user).select_related('ingredient')
    
    # Group preferences by type
    preferences_by_type = {}
    for pref_type, _ in MealPreference.PREFERENCE_TYPES:
        preferences_by_type[pref_type] = preferences.filter(preference_type=pref_type)
    
    context = {
        'preferences_by_type': preferences_by_type,
        'preference_types': MealPreference.PREFERENCE_TYPES,
        'total_preferences': preferences.count(),
    }
    
    return render(request, 'meals/preferences.html', context)


@login_required
def ingredients_page(request):
    """Ingredients browsing page"""
    ingredients = Ingredient.objects.all().select_related('category')
    categories = Category.objects.all()
    
    # Get search query
    query = request.GET.get('q', '')
    if query:
        ingredients = ingredients.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Get user's preferences to show which ingredients they already have preferences for
    user_preferences = MealPreference.objects.filter(user=request.user)
    preferred_ingredient_ids = user_preferences.values_list('ingredient_id', flat=True)
    
    context = {
        'ingredients': ingredients,
        'categories': categories,
        'query': query,
        'preferred_ingredient_ids': list(preferred_ingredient_ids),
        'user_preferences': {p.ingredient_id: p.preference_type for p in user_preferences},
    }
    
    return render(request, 'meals/ingredients.html', context)


class DietListView(generics.ListCreateAPIView):
    """List and create diets for the authenticated user"""
    serializer_class = DietSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Diet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DietDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific diet"""
    serializer_class = DietSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Diet.objects.filter(user=self.request.user)


class MealListView(generics.ListCreateAPIView):
    """List and create meals"""
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meal.objects.filter(diet__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the diet belongs to the user
        diet_id = self.request.data.get('diet_id')
        diet = get_object_or_404(Diet, id=diet_id, user=self.request.user)
        serializer.save(diet=diet)


class MealDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific meal"""
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Meal.objects.filter(diet__user=self.request.user)


class CategoryListView(generics.ListCreateAPIView):
    """List and create ingredient categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class IngredientListView(generics.ListCreateAPIView):
    """List and create ingredients"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]


class IngredientSearchView(generics.ListAPIView):
    """Search ingredients by name"""
    serializer_class = IngredientSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Ingredient.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )[:20]
        return Ingredient.objects.none()


class MealIngredientListView(generics.ListCreateAPIView):
    """List and create meal ingredients"""
    serializer_class = MealIngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        meal_id = self.kwargs.get('meal_id')
        return MealIngredient.objects.filter(
            meal_id=meal_id,
            meal__diet__user=self.request.user
        )

    def perform_create(self, serializer):
        meal_id = self.kwargs.get('meal_id')
        meal = get_object_or_404(Meal, id=meal_id, diet__user=self.request.user)
        serializer.save(meal=meal)


class MealIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific meal ingredient"""
    serializer_class = MealIngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MealIngredient.objects.filter(
            meal__diet__user=self.request.user
        )


class MealRecordListView(generics.ListCreateAPIView):
    """List and create meal records"""
    serializer_class = MealRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MealRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MealRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific meal record"""
    serializer_class = MealRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MealRecord.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class MealPreferenceListView(generics.ListCreateAPIView):
    """List and create meal preferences for the authenticated user"""
    serializer_class = MealPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MealPreference.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MealPreferenceCreateSerializer
        return MealPreferenceSerializer

    def perform_create(self, serializer):
        # Handle ingredient creation if ingredient_name is provided
        ingredient_name = self.request.data.get('ingredient_name')
        print(f"Creating preference for user: {self.request.user.username}")
        print(f"Ingredient name: {ingredient_name}")
        print(f"Request data: {self.request.data}")
        
        if ingredient_name:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_name,
                defaults={
                    'proteins': 0.0,
                    'fats': 0.0,
                    'carbs': 0.0,
                    'calories': 0.0,
                    'fibers': 0.0,
                    'sugars': 0.0,
                }
            )
            print(f"Ingredient: {ingredient.name} (created: {created})")
            preference = serializer.save(user=self.request.user, ingredient=ingredient)
            print(f"Preference created: {preference.id}")
        else:
            preference = serializer.save(user=self.request.user)
            print(f"Preference created: {preference.id}")


class MealPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific meal preference"""
    serializer_class = MealPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MealPreference.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MealPreferenceUpdateSerializer
        return MealPreferenceSerializer


class MealPreferenceByTypeView(generics.ListAPIView):
    """List meal preferences filtered by preference type"""
    serializer_class = MealPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        preference_type = self.kwargs.get('preference_type')
        return MealPreference.objects.filter(
            user=self.request.user,
            preference_type=preference_type
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_meal_preferences_summary(request):
    """Get a summary of user's meal preferences"""
    preferences = MealPreference.objects.filter(user=request.user)
    
    summary = {
        'total_preferences': preferences.count(),
        'by_type': {},
        'recent_additions': []
    }
    
    # Group by preference type
    for pref_type, _ in MealPreference.PREFERENCE_TYPES:
        count = preferences.filter(preference_type=pref_type).count()
        summary['by_type'][pref_type] = count
    
    # Get recent additions
    recent = preferences.order_by('-created_at')[:5]
    summary['recent_additions'] = MealPreferenceSerializer(recent, many=True).data
    
    return Response(summary)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_meal_preferences(request):
    """Bulk update meal preferences"""
    preferences_data = request.data.get('preferences', [])
    updated_count = 0
    
    for pref_data in preferences_data:
        preference_id = pref_data.get('id')
        preference_type = pref_data.get('preference_type')
        description = pref_data.get('description')
        
        try:
            preference = MealPreference.objects.get(
                id=preference_id,
                user=request.user
            )
            
            if preference_type:
                preference.preference_type = preference_type
            if description is not None:
                preference.description = description
                
            preference.save()
            updated_count += 1
            
        except MealPreference.DoesNotExist:
            continue
    
    return Response({
        'message': f'Successfully updated {updated_count} preferences',
        'updated_count': updated_count
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_meal_preference(request, preference_id):
    """Delete a specific meal preference"""
    try:
        preference = MealPreference.objects.get(
            id=preference_id,
            user=request.user
        )
        preference.delete()
        return Response({'message': 'Preference deleted successfully'})
    except MealPreference.DoesNotExist:
        return Response(
            {'error': 'Preference not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ingredient_suggestions(request):
    """Get ingredient suggestions based on user preferences"""
    query = request.query_params.get('q', '')
    if not query:
        return Response({'suggestions': []})
    
    # Get ingredients that match the query
    ingredients = Ingredient.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query)
    )
    
    # Get user's existing preferences (if authenticated)
    existing_ingredient_ids = []
    if request.user.is_authenticated:
        user_preferences = MealPreference.objects.filter(user=request.user)
        existing_ingredient_ids = user_preferences.values_list('ingredient_id', flat=True)
    
    # Filter out ingredients the user already has preferences for and limit to 10
    suggestions = ingredients.exclude(id__in=existing_ingredient_ids)[:10]
    
    return Response({
        'suggestions': IngredientSearchSerializer(suggestions, many=True).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def quick_preference_update(request):
    """Quick update or create a preference for an ingredient"""
    ingredient_id = request.data.get('ingredient_id')
    preference_type = request.data.get('preference_type')
    
    if not ingredient_id or not preference_type:
        return Response(
            {'error': 'ingredient_id and preference_type are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
    except Ingredient.DoesNotExist:
        return Response(
            {'error': 'Ingredient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if preference already exists
    preference, created = MealPreference.objects.get_or_create(
        user=request.user,
        ingredient=ingredient,
        defaults={'preference_type': preference_type}
    )
    
    if not created:
        # Update existing preference
        preference.preference_type = preference_type
        preference.save()
    
    return Response({
        'id': preference.id,
        'ingredient_id': ingredient_id,
        'preference_type': preference_type,
        'created': created,
        'message': 'Preference updated successfully'
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def quick_preference_delete(request, ingredient_id):
    """Delete a preference for an ingredient"""
    try:
        preference = MealPreference.objects.get(
            user=request.user,
            ingredient_id=ingredient_id
        )
        preference.delete()
        return Response({'message': 'Preference deleted successfully'})
    except MealPreference.DoesNotExist:
        return Response(
            {'error': 'Preference not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_ingredient(request):
    """Create a new ingredient"""
    serializer = IngredientSerializer(data=request.data)
    if serializer.is_valid():
        ingredient = serializer.save()
        return Response({
            'id': ingredient.id,
            'name': ingredient.name,
            'message': 'Ingredient created successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_ingredient(request, ingredient_id):
    """Update an existing ingredient"""
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
    except Ingredient.DoesNotExist:
        return Response(
            {'error': 'Ingredient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = IngredientSerializer(ingredient, data=request.data, partial=True)
    if serializer.is_valid():
        ingredient = serializer.save()
        return Response({
            'id': ingredient.id,
            'name': ingredient.name,
            'message': 'Ingredient updated successfully'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ingredient(request, ingredient_id):
    """Get ingredient details for editing"""
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
        serializer = IngredientSerializer(ingredient)
        return Response(serializer.data)
    except Ingredient.DoesNotExist:
        return Response(
            {'error': 'Ingredient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@login_required
def meals_management_page(request):
    """Meals management page"""
    user = request.user
    
    # Get user's diets and meals
    diets = Diet.objects.filter(user=user)
    
    # Get selected diet filter
    selected_diet_id = request.GET.get('diet')
    
    # Get active diet
    active_diet = diets.filter(is_active=True).first()
    
    # Filter meals by diet if specified
    if selected_diet_id:
        meals = Meal.objects.filter(diet__user=user, diet_id=selected_diet_id).select_related('diet').prefetch_related('mealingredient_set__ingredient')
    else:
        # Use active diet if available, otherwise show all meals
        if active_diet:
            meals = Meal.objects.filter(diet__user=user, diet=active_diet).select_related('diet').prefetch_related('mealingredient_set__ingredient')
            selected_diet_id = active_diet.id
        else:
            meals = Meal.objects.filter(diet__user=user).select_related('diet').prefetch_related('mealingredient_set__ingredient')
    
    # Get all ingredients for the ingredient selector
    ingredients = Ingredient.objects.all().select_related('category')
    
    # Get categories for filtering
    categories = Category.objects.all()
    
    context = {
        'diets': diets,
        'meals': meals,
        'ingredients': ingredients,
        'categories': categories,
        'selected_diet_id': selected_diet_id,
    }
    
    return render(request, 'meals/meals.html', context)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_meal(request):
    """Create a new meal"""
    serializer = MealSerializer(data=request.data)
    if serializer.is_valid():
        # Get the diet
        diet_id = request.data.get('diet_id')
        try:
            diet = Diet.objects.get(id=diet_id, user=request.user)
        except Diet.DoesNotExist:
            return Response(
                {'error': 'Diet not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        meal = serializer.save(diet=diet)
        return Response({
            'id': meal.id,
            'name': meal.name,
            'message': 'Meal created successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_meal(request, meal_id):
    """Update an existing meal"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MealSerializer(meal, data=request.data, partial=True)
    if serializer.is_valid():
        meal = serializer.save()
        return Response({
            'id': meal.id,
            'name': meal.name,
            'message': 'Meal updated successfully'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_meal(request, meal_id):
    """Get meal details for editing"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
        # Use the simplified serializer to avoid Goal serialization issues
        from .serializers import MealEditSerializer
        serializer = MealEditSerializer(meal)
        return Response(serializer.data)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_meal(request, meal_id):
    """Delete a meal"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
        meal.delete()
        return Response({'message': 'Meal deleted successfully'})
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_ingredient_to_meal(request, meal_id):
    """Add an ingredient to a meal"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    ingredient_id = request.data.get('ingredient_id')
    quantity = request.data.get('quantity', 100)  # Default to 100g
    
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
    except Ingredient.DoesNotExist:
        return Response(
            {'error': 'Ingredient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if ingredient already exists in meal
    existing = MealIngredient.objects.filter(meal=meal, ingredient=ingredient).first()
    if existing:
        return Response(
            {'error': 'Ingredient already exists in this meal'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    meal_ingredient = MealIngredient.objects.create(
        meal=meal,
        ingredient=ingredient,
        quantity=quantity,
        unit='g'
    )
    
    return Response({
        'id': meal_ingredient.id,
        'ingredient_name': ingredient.name,
        'quantity': quantity,
        'message': 'Ingredient added successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_meal_ingredient(request, meal_ingredient_id):
    """Update meal ingredient quantity"""
    try:
        meal_ingredient = MealIngredient.objects.get(
            id=meal_ingredient_id,
            meal__diet__user=request.user
        )
    except MealIngredient.DoesNotExist:
        return Response(
            {'error': 'Meal ingredient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    quantity = request.data.get('quantity')
    if quantity is not None:
        meal_ingredient.quantity = quantity
        meal_ingredient.save()
        
        return Response({
            'id': meal_ingredient.id,
            'quantity': quantity,
            'message': 'Quantity updated successfully'
        })
    
    return Response(
        {'error': 'Quantity is required'}, 
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_ingredient_from_meal(request, meal_ingredient_id):
    """Remove an ingredient from a meal"""
    try:
        meal_ingredient = MealIngredient.objects.get(
            id=meal_ingredient_id,
            meal__diet__user=request.user
        )
        meal_ingredient.delete()
        return Response({'message': 'Ingredient removed successfully'})
    except MealIngredient.DoesNotExist:
        return Response(
            {'error': 'Meal ingredient not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_active_diet(request, diet_id):
    """Set a diet as active for the user"""
    try:
        diet = Diet.objects.get(id=diet_id, user=request.user)
        diet.is_active = True
        diet.save()  # This will automatically deactivate other diets
        return Response({
            'id': diet.id,
            'name': diet.name,
            'message': 'Diet set as active successfully'
        })
    except Diet.DoesNotExist:
        return Response(
            {'error': 'Diet not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def schedule_meal(request, meal_id):
    """Schedule a meal and sync to Google Calendar"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update meal scheduling
    meal.is_scheduled = request.data.get('is_scheduled', True)
    
    # Handle date field
    start_date_str = request.data.get('start_date')
    if start_date_str:
        from datetime import datetime
        meal.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    
    # Handle time field
    start_time_str = request.data.get('start_time')
    if start_time_str:
        from datetime import datetime
        meal.start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    
    meal.duration_minutes = request.data.get('duration_minutes', 30)
    meal.recurrence_type = request.data.get('recurrence_type', 'none')
    
    # Handle recurrence_until field
    recurrence_until_str = request.data.get('recurrence_until')
    if recurrence_until_str:
        from datetime import datetime
        meal.recurrence_until = datetime.strptime(recurrence_until_str, '%Y-%m-%d').date()
    
    meal.meal_type = request.data.get('meal_type', 'regular')
    
    meal.save()
    
    # Sync to Google Calendar
    from .services import sync_meal_to_calendar
    calendar_event_id = sync_meal_to_calendar(meal)
    
    return Response({
        'id': meal.id,
        'name': meal.name,
        'is_scheduled': meal.is_scheduled,
        'calendar_event_id': calendar_event_id,
        'message': 'Meal scheduled successfully'
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unschedule_meal(request, meal_id):
    """Unschedule a meal and remove from Google Calendar"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Remove from Google Calendar
    from .services import sync_meal_to_calendar
    sync_meal_to_calendar(meal)  # This will delete the event
    
    # Clear scheduling
    meal.is_scheduled = False
    meal.start_date = None
    meal.start_time = None
    meal.recurrence_type = 'none'
    meal.recurrence_until = None
    meal.google_calendar_event_id = ""
    meal.save()
    
    return Response({
        'id': meal.id,
        'name': meal.name,
        'message': 'Meal unscheduled successfully'
    })
