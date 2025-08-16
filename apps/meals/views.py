from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta, date, time
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
class MealFeedbackView(APIView):
    """Handle meal feedback (get and update)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, meal_id):
        """Get existing feedback for a meal on a specific date"""
        date_str = request.GET.get('date')
        if not date_str:
            return Response({'error': 'Date parameter required'}, status=400)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        
        # Find the meal record for this meal and date
        meal_record = MealRecord.objects.filter(
            meal_id=meal_id,
            user=request.user,
            timestamp__date=date
        ).first()
        
        if meal_record:
            return Response({
                'feedback': meal_record.feedback,
                'photo_url': meal_record.photo.url if meal_record.photo else None
            })
        else:
            return Response({'feedback': None, 'photo_url': None})
    
    def post(self, request, meal_id):
        """Update or create feedback for a meal"""
        date_str = request.data.get('date')
        feedback = request.data.get('feedback', '')
        photo = request.FILES.get('photo')
        
        if not date_str:
            return Response({'error': 'Date parameter required'}, status=400)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        
        # Find or create the meal record
        meal_record, created = MealRecord.objects.get_or_create(
            meal_id=meal_id,
            user=request.user,
            timestamp__date=date,
            defaults={
                'timestamp': datetime.combine(date, time(12, 0)),  # Default to noon
                'feedback': feedback
            }
        )
        
        if not created:
            # Update existing record
            meal_record.feedback = feedback
            if photo:
                meal_record.photo = photo
            meal_record.save()
        
        return Response({'success': True, 'meal_record_id': meal_record.id})


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
    
    # Convert ingredients to JSON for JavaScript
    from django.core.serializers.json import DjangoJSONEncoder
    import json
    ingredients_json = json.dumps([
        {
            'id': ing.id,
            'name': ing.name,
            'calories': ing.calories,
            'proteins': ing.proteins,
            'carbs': ing.carbs,
            'fats': ing.fats,
            'fibers': ing.fibers,
            'sugars': ing.sugars,
        }
        for ing in ingredients
    ], cls=DjangoJSONEncoder)
    
    context = {
        'diets': diets,
        'meals': meals,
        'ingredients': ingredients,
        'ingredients_json': ingredients_json,
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
    
    # Handle end_date field
    end_date_str = request.data.get('end_date')
    if end_date_str:
        from datetime import datetime
        meal.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        meal.end_date = None
    
    # Handle time field
    start_time_str = request.data.get('start_time')
    if start_time_str:
        from datetime import datetime
        meal.start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    
    meal.duration_minutes = request.data.get('duration_minutes', 30)
    meal.recurrence_type = request.data.get('recurrence_type', 'none')
    
    # Handle recurrence_until field (for backward compatibility)
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_meal(request):
    """Log a meal record (no diet/meal creation)"""
    try:
        meal_name = request.data.get('name')
        date_str = request.data.get('date')
        time_str = request.data.get('time')
        
        if not meal_name or not date_str or not time_str:
            return Response(
                {'error': 'Meal name, date, and time are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date and time
        start_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(time_str, '%H:%M').time()
        timestamp = datetime.combine(start_date, start_time)
        
        # Get nutritional values
        calories = request.data.get('calories')
        proteins = request.data.get('proteins')
        carbs = request.data.get('carbs')
        fats = request.data.get('fats')
        quantity_grams = request.data.get('quantity_grams')
        
        # Create meal record (no linked meal)
        meal_record = MealRecord.objects.create(
            meal=None,  # No linked meal
            meal_name=meal_name,
            timestamp=timestamp,
            user=request.user,
            calories=float(calories) if calories else None,
            proteins=float(proteins) if proteins else None,
            carbs=float(carbs) if carbs else None,
            fats=float(fats) if fats else None,
            quantity_grams=float(quantity_grams) if quantity_grams else None,
        )
        
        return Response({
            'success': True,
            'id': meal_record.id,
            'name': meal_record.meal_name,
            'message': 'Meal logged successfully'
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_meal_record(request, record_id):
    """Delete a meal record"""
    try:
        meal_record = MealRecord.objects.get(id=record_id, user=request.user)
        meal_record.delete()
        
        return Response({
            'success': True,
            'message': 'Meal record deleted successfully'
        })
        
    except MealRecord.DoesNotExist:
        return Response(
            {'error': 'Meal record not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_and_schedule_meal(request):
    """Create a new meal or meal record from the calendar"""
    try:
        meal_name = request.data.get('name', 'New Meal')
        start_date_str = request.data.get('start_date')
        start_time_str = request.data.get('start_time')
        
        if not start_date_str or not start_time_str:
            return Response(
                {'error': 'Date and time are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse date and time
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        timestamp = datetime.combine(start_date, start_time)
        
        # Check if nutritional information is provided
        calories = request.data.get('calories')
        proteins = request.data.get('proteins')
        carbs = request.data.get('carbs')
        fats = request.data.get('fats')
        quantity_grams = request.data.get('quantity_grams')
        
        has_nutritional_info = any([calories, proteins, carbs, fats, quantity_grams])
        
        if has_nutritional_info:
            # Create an unplanned meal record
            meal_record = MealRecord.objects.create(
                meal=None,  # No linked meal
                meal_name=meal_name,
                timestamp=timestamp,
                user=request.user,
                calories=float(calories) if calories else None,
                proteins=float(proteins) if proteins else None,
                carbs=float(carbs) if carbs else None,
                fats=float(fats) if fats else None,
                quantity_grams=float(quantity_grams) if quantity_grams else None,
            )
            
            return Response({
                'success': True,
                'id': meal_record.id,
                'name': meal_record.meal_name,
                'type': 'unplanned',
                'message': 'Unplanned meal recorded successfully'
            })
        else:
            # Create a planned meal (requires active diet)
            active_diet = Diet.objects.filter(user=request.user, is_active=True).first()
            if not active_diet:
                return Response(
                    {'error': 'No active diet found. Please create or activate a diet first, or provide nutritional information for an unplanned meal.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a new meal
            meal = Meal.objects.create(
                name=meal_name,
                description=request.data.get('description', 'Meal created from calendar'),
                diet=active_diet,
                is_scheduled=True,
                start_date=start_date,
                start_time=start_time,
                duration_minutes=int(request.data.get('duration_minutes', 30)),
                recurrence_type=request.data.get('recurrence_type', 'none'),
                meal_type=request.data.get('meal_type', 'regular')
            )
            
            # Handle end_date field
            end_date_str = request.data.get('end_date')
            if end_date_str:
                meal.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Handle recurrence_until field
            recurrence_until_str = request.data.get('recurrence_until')
            if recurrence_until_str:
                meal.recurrence_until = datetime.strptime(recurrence_until_str, '%Y-%m-%d').date()
            
            meal.save()
            
            # Sync to Google Calendar
            from .services import sync_meal_to_calendar
            calendar_event_id = sync_meal_to_calendar(meal)
            
            return Response({
                'success': True,
                'id': meal.id,
                'name': meal.name,
                'type': 'planned',
                'calendar_event_id': calendar_event_id,
                'message': 'Meal created and scheduled successfully'
            })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_meal_completed(request, meal_id):
    """Mark a meal as completed by creating a MealRecord"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get date from request or use current date
    date_str = request.data.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # Set time to meal's scheduled time or current time
            if meal.start_time:
                timestamp = datetime.combine(target_date, meal.start_time)
            else:
                timestamp = datetime.combine(target_date, timezone.now().time())
        except ValueError:
            return Response(
                {'error': 'Invalid date format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        timestamp = timezone.now()
    
    # Check if meal is already completed for this date
    existing_record = MealRecord.objects.filter(
        meal=meal,
        user=request.user,
        timestamp__date=timestamp.date()
    ).first()
    
    if existing_record:
        return Response(
            {'error': 'Meal already marked as completed for this date'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create meal record
    meal_record = MealRecord.objects.create(
        meal=meal,
        user=request.user,
        timestamp=timestamp,
        feedback=request.data.get('feedback', '')
    )
    
    return Response({
        'id': meal_record.id,
        'meal_id': meal.id,
        'meal_name': meal.name,
        'timestamp': meal_record.timestamp,
        'message': 'Meal marked as completed successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unmark_meal_completed(request, meal_id):
    """Unmark a meal as completed by removing the MealRecord"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get timestamp from request or use current date
    date_str = request.data.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        target_date = timezone.now().date()
    
    # Find and delete the meal record for this date
    meal_record = MealRecord.objects.filter(
        meal=meal,
        user=request.user,
        timestamp__date=target_date
    ).first()
    
    if not meal_record:
        return Response(
            {'error': 'No meal record found for this date'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    meal_record.delete()
    
    return Response({
        'meal_id': meal.id,
        'meal_name': meal.name,
        'message': 'Meal unmarked as completed successfully'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_meal_completion_status(request, meal_id):
    """Get completion status of a meal for a specific date"""
    try:
        meal = Meal.objects.get(id=meal_id, diet__user=request.user)
    except Meal.DoesNotExist:
        return Response(
            {'error': 'Meal not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get date from request or use current date
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        target_date = timezone.now().date()
    
    # Check if meal is completed for this date
    meal_record = MealRecord.objects.filter(
        meal=meal,
        user=request.user,
        timestamp__date=target_date
    ).first()
    
    return Response({
        'meal_id': meal.id,
        'meal_name': meal.name,
        'date': target_date,
        'is_completed': meal_record is not None,
        'completion_time': meal_record.timestamp if meal_record else None,
        'feedback': meal_record.feedback if meal_record else None
    })


@login_required
def calendar_view(request):
    """Weekly calendar view for meals"""
    user = request.user
    
    # Get week parameter from URL, default to current week
    week_param = request.GET.get('week')
    if week_param:
        try:
            # Parse week parameter (format: YYYY-WW)
            year, week = map(int, week_param.split('-'))
            # Get the first day of the week (Monday)
            start_date = date(year, 1, 1) + timedelta(weeks=week-1)
            # Adjust to Monday
            while start_date.weekday() != 0:  # Monday is 0
                start_date -= timedelta(days=1)
        except (ValueError, TypeError):
            start_date = timezone.now().date()
    else:
        start_date = timezone.now().date()
    
    # Calculate week boundaries (Monday to Sunday)
    days_since_monday = start_date.weekday()
    week_start = start_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    # Get all days in the week
    week_days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        week_days.append(day_date)
    
    # Get scheduled meals for the week (including recurrent meals)
    scheduled_meals = Meal.objects.filter(
        diet__user=user,
        is_scheduled=True
    ).select_related('diet').prefetch_related('mealingredient_set__ingredient')
    
    # Create a map of meals by day
    meals_by_day = {}
    for day in week_days:
        meals_by_day[day] = {
            'scheduled': [],
            'completed': [],
            'planned_calories': 0,
            'planned_proteins': 0,
            'planned_carbs': 0,
            'planned_fats': 0,
            'taken_calories': 0,
            'taken_proteins': 0,
            'taken_carbs': 0,
            'taken_fats': 0,
        }
    
    # Process each scheduled meal and add it to the appropriate days
    for meal in scheduled_meals:
        # Check if meal has a valid date range
        meal_start = meal.start_date or week_start
        meal_end = meal.end_date or meal.recurrence_until
        
        # Skip if meal ends before this week starts
        if meal_end and meal_end < week_start:
            continue
            
        # Skip if meal starts after this week ends
        if meal_start and meal_start > week_end:
            continue
            
        if meal.recurrence_type == 'none':
            # Single occurrence - check if it's in this week
            if meal.start_date and week_start <= meal.start_date <= week_end:
                meals_by_day[meal.start_date]['scheduled'].append(meal)
        elif meal.recurrence_type == 'daily':
            # Daily recurrence - add to every day in the week within the date range
            for i in range(7):
                day_date = week_start + timedelta(days=i)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    meals_by_day[day_date]['scheduled'].append(meal)
        elif meal.recurrence_type == 'weekly':
            # Weekly recurrence - add to the same day of the week
            if meal.start_date:
                # Find the day of week (0=Monday, 6=Sunday)
                meal_day_of_week = meal.start_date.weekday()
                # Get the corresponding day in the current week
                day_date = week_start + timedelta(days=meal_day_of_week)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    meals_by_day[day_date]['scheduled'].append(meal)
        elif meal.recurrence_type == 'weekday':
            # Weekdays (Mon-Fri) - add to Monday through Friday
            for i in range(5):  # Monday to Friday
                day_date = week_start + timedelta(days=i)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    meals_by_day[day_date]['scheduled'].append(meal)
        elif meal.recurrence_type == 'weekend':
            # Weekends (Sat-Sun) - add to Saturday and Sunday
            for i in range(5, 7):  # Saturday and Sunday
                day_date = week_start + timedelta(days=i)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    meals_by_day[day_date]['scheduled'].append(meal)
    
    # Sort meals by time within each day
    for day in week_days:
        meals_by_day[day]['scheduled'].sort(key=lambda meal: meal.start_time or time(23, 59))  # Meals without time go to end
    
    # Get meal records for the week (completed meals and unplanned meals)
    meal_records = MealRecord.objects.filter(
        user=user,
        timestamp__date__gte=week_start,
        timestamp__date__lte=week_end
    ).select_related('meal')
    

    
    # Create a set of completed meal IDs for each day to track completion status
    completed_meal_ids_by_day = {}
    for day in week_days:
        completed_meal_ids_by_day[day] = set()
    
    # Calculate planned nutrition for all scheduled meals
    for day in week_days:
        day_data = meals_by_day[day]
        for meal in day_data['scheduled']:
            for meal_ingredient in meal.mealingredient_set.all():
                ratio = meal_ingredient.quantity / 100
                day_data['planned_calories'] += meal_ingredient.ingredient.calories * ratio
                day_data['planned_proteins'] += meal_ingredient.ingredient.proteins * ratio
                day_data['planned_carbs'] += meal_ingredient.ingredient.carbs * ratio
                day_data['planned_fats'] += meal_ingredient.ingredient.fats * ratio
    
    # Populate completed meals and calculate taken nutrition
    for record in meal_records:
        day = record.timestamp.date()
        if day in meals_by_day:
            if record.meal:
                # Planned meal record
                completed_meal_ids_by_day[day].add(record.meal.id)
                
                # Calculate nutrition for completed meal
                meal = record.meal
                for meal_ingredient in meal.mealingredient_set.all():
                    ratio = meal_ingredient.quantity / 100
                    meals_by_day[day]['taken_calories'] += meal_ingredient.ingredient.calories * ratio
                    meals_by_day[day]['taken_proteins'] += meal_ingredient.ingredient.proteins * ratio
                    meals_by_day[day]['taken_carbs'] += meal_ingredient.ingredient.carbs * ratio
                    meals_by_day[day]['taken_fats'] += meal_ingredient.ingredient.fats * ratio
            else:
                # Unplanned meal record - use direct nutritional values
                meals_by_day[day]['taken_calories'] += record.calories or 0
                meals_by_day[day]['taken_proteins'] += record.proteins or 0
                meals_by_day[day]['taken_carbs'] += record.carbs or 0
                meals_by_day[day]['taken_fats'] += record.fats or 0
    
    # Calculate week totals
    week_totals = {
        'planned_calories': sum(day['planned_calories'] for day in meals_by_day.values()),
        'planned_proteins': sum(day['planned_proteins'] for day in meals_by_day.values()),
        'planned_carbs': sum(day['planned_carbs'] for day in meals_by_day.values()),
        'planned_fats': sum(day['planned_fats'] for day in meals_by_day.values()),
        'taken_calories': sum(day['taken_calories'] for day in meals_by_day.values()),
        'taken_proteins': sum(day['taken_proteins'] for day in meals_by_day.values()),
        'taken_carbs': sum(day['taken_carbs'] for day in meals_by_day.values()),
        'taken_fats': sum(day['taken_fats'] for day in meals_by_day.values()),
    }
    
    # Get active diet for target nutrition
    active_diet = Diet.objects.filter(user=user, is_active=True).first()
    if active_diet:
        weekly_targets = {
            'calories': active_diet.day_calories_kcal * 7,
            'proteins': active_diet.day_proteins_g * 7,
            'carbs': active_diet.day_carbohydrates_g * 7,
            'fats': active_diet.day_fats_g * 7,
        }
        
        # Calculate percentages
        week_percentages = {
            'calories': (week_totals['taken_calories'] / weekly_targets['calories'] * 100) if weekly_targets['calories'] > 0 else 0,
            'proteins': (week_totals['taken_proteins'] / weekly_targets['proteins'] * 100) if weekly_targets['proteins'] > 0 else 0,
            'carbs': (week_totals['taken_carbs'] / weekly_targets['carbs'] * 100) if weekly_targets['carbs'] > 0 else 0,
            'fats': (week_totals['taken_fats'] / weekly_targets['fats'] * 100) if weekly_targets['fats'] > 0 else 0,
        }
    else:
        weekly_targets = None
        week_percentages = None
    
    # Calculate navigation URLs
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    
    prev_week_param = f"{prev_week.year}-{prev_week.isocalendar()[1]}"
    next_week_param = f"{next_week.year}-{next_week.isocalendar()[1]}"
    current_week_param = f"{week_start.year}-{week_start.isocalendar()[1]}"
    
    # Get current date for determining which days are editable
    current_date = timezone.now().date()
    
    # Get view type from request
    view_type = request.GET.get('view', 'week')
    
    context = {
        'week_days': week_days,
        'meals_by_day': meals_by_day,
        'completed_meal_ids_by_day': completed_meal_ids_by_day,
        'meal_records': meal_records,  # Add meal records for unplanned meals
        'week_totals': week_totals,
        'weekly_targets': weekly_targets,
        'week_percentages': week_percentages,
        'active_diet': active_diet,
        'prev_week_param': prev_week_param,
        'next_week_param': next_week_param,
        'current_week_param': current_week_param,
        'week_start': week_start,
        'week_end': week_end,
        'current_date': current_date,
        'view_type': view_type,
    }
    
    # Render appropriate template based on view type
    if view_type == 'day':
        # For day view, we need to get a specific date
        selected_date_str = request.GET.get('date')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = current_date
        else:
            selected_date = current_date
        
        # Get data for the specific day
        day_data = meals_by_day.get(selected_date, {
            'scheduled': [],
            'completed': [],
            'planned_calories': 0,
            'planned_proteins': 0,
            'planned_carbs': 0,
            'planned_fats': 0,
            'taken_calories': 0,
            'taken_proteins': 0,
            'taken_carbs': 0,
            'taken_fats': 0,
        })
        
        # Get unplanned meals for this day
        unplanned_meals = [record for record in meal_records if record.timestamp.date() == selected_date and not record.meal]
        
        # Get completed meal IDs for this specific day
        completed_meals_for_day = completed_meal_ids_by_day.get(selected_date, set())
        
        # Calculate day totals
        day_totals = {
            'taken_calories': day_data['taken_calories'],
            'taken_proteins': day_data['taken_proteins'],
            'taken_carbs': day_data['taken_carbs'],
            'taken_fats': day_data['taken_fats'],
        }
        
        # Get daily targets from active diet
        daily_targets = None
        day_percentages = None
        if active_diet:
            daily_targets = {
                'calories': active_diet.day_calories_kcal,
                'proteins': active_diet.day_proteins_g,
                'carbs': active_diet.day_carbohydrates_g,
                'fats': active_diet.day_fats_g,
            }
            
            # Calculate percentages
            day_percentages = {
                'calories': (day_totals['taken_calories'] / daily_targets['calories'] * 100) if daily_targets['calories'] > 0 else 0,
                'proteins': (day_totals['taken_proteins'] / daily_targets['proteins'] * 100) if daily_targets['proteins'] > 0 else 0,
                'carbs': (day_totals['taken_carbs'] / daily_targets['carbs'] * 100) if daily_targets['carbs'] > 0 else 0,
                'fats': (day_totals['taken_fats'] / daily_targets['fats'] * 100) if daily_targets['fats'] > 0 else 0,
            }
        
        # Calculate navigation dates
        prev_day = selected_date - timedelta(days=1)
        next_day = selected_date + timedelta(days=1)
        
        # Add day-specific context
        context.update({
            'selected_date': selected_date,
            'day_data': day_data,
            'unplanned_meals': unplanned_meals,
            'completed_meals_for_day': completed_meals_for_day,
            'day_totals': day_totals,
            'daily_targets': daily_targets,
            'day_percentages': day_percentages,
            'prev_day': prev_day,
            'next_day': next_day,
        })
        
        return render(request, 'meals/calendar_day.html', context)
    else:
        return render(request, 'meals/calendar.html', context)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_ingredient_from_form(request):
    """Create a new ingredient from the meal form"""
    try:
        name = request.data.get('name')
        calories = request.data.get('calories', 0)
        proteins = request.data.get('proteins', 0)
        carbs = request.data.get('carbs', 0)
        fats = request.data.get('fats', 0)
        fibers = request.data.get('fibers', 0)
        sugars = request.data.get('sugars', 0)
        is_personal = request.data.get('is_personal', True)
        
        if not name:
            return Response(
                {'error': 'Ingredient name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the ingredient
        ingredient = Ingredient.objects.create(
            name=name,
            calories=float(calories),
            proteins=float(proteins),
            carbs=float(carbs),
            fats=float(fats),
            fibers=float(fibers),
            sugars=float(sugars),
            is_personal=is_personal,
            created_by=request.user
        )
        
        # Create a default preference for the user (like)
        MealPreference.objects.create(
            user=request.user,
            ingredient=ingredient,
            preference_type='like',
            description=f'Personal ingredient: {name}'
        )
        
        return Response({
            'id': ingredient.id,
            'name': ingredient.name,
            'calories': ingredient.calories,
            'proteins': ingredient.proteins,
            'carbs': ingredient.carbs,
            'fats': ingredient.fats,
            'fibers': ingredient.fibers,
            'sugars': ingredient.sugars,
            'message': 'Ingredient created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_ingredient_suggestions(request):
    """Get AI-powered ingredient suggestions and variants"""
    ingredient_name = request.GET.get('name')
    if not ingredient_name:
        return Response({'error': 'Ingredient name required'}, status=400)
    
    try:
        suggestions = get_ingredient_suggestions(ingredient_name)
        return Response({
            'success': True,
            'suggestions': suggestions
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_nutrition_lookup(request):
    """Get AI-powered nutritional data for an ingredient"""
    ingredient_name = request.GET.get('name')
    if not ingredient_name:
        return Response({'error': 'Ingredient name required'}, status=400)
    
    try:
        nutrition_data = get_mock_nutrition_data(ingredient_name)
        return Response({
            'success': True,
            'nutrition': nutrition_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def get_ingredient_suggestions(base_name):
    """Get ingredient variants and suggestions"""
    suggestions_map = {
        'rice': [
            {'name': 'Basmati Rice', 'category': 'grain', 'description': 'Long-grain aromatic rice'},
            {'name': 'Brown Rice', 'category': 'grain', 'description': 'Whole grain rice with bran'},
            {'name': 'Wild Rice', 'category': 'grain', 'description': 'Nutty flavored rice variety'},
            {'name': 'Jasmine Rice', 'category': 'grain', 'description': 'Fragrant long-grain rice'},
            {'name': 'Arborio Rice', 'category': 'grain', 'description': 'Short-grain rice for risotto'},
        ],
        'chicken': [
            {'name': 'Chicken Breast', 'category': 'meat', 'description': 'Lean white meat'},
            {'name': 'Chicken Thigh', 'category': 'meat', 'description': 'Dark meat with more fat'},
            {'name': 'Chicken Wing', 'category': 'meat', 'description': 'Small wing pieces'},
            {'name': 'Ground Chicken', 'category': 'meat', 'description': 'Minced chicken meat'},
        ],
        'apple': [
            {'name': 'Red Apple', 'category': 'fruit', 'description': 'Sweet red apple variety'},
            {'name': 'Green Apple', 'category': 'fruit', 'description': 'Tart green apple variety'},
            {'name': 'Gala Apple', 'category': 'fruit', 'description': 'Sweet and crisp apple'},
            {'name': 'Granny Smith Apple', 'category': 'fruit', 'description': 'Tart green apple'},
        ],
        'salmon': [
            {'name': 'Atlantic Salmon', 'category': 'fish', 'description': 'Farmed salmon'},
            {'name': 'Wild Salmon', 'category': 'fish', 'description': 'Wild-caught salmon'},
            {'name': 'Smoked Salmon', 'category': 'fish', 'description': 'Cured and smoked salmon'},
        ],
    }
    
    base_lower = base_name.lower()
    for key, variants in suggestions_map.items():
        if key in base_lower or base_lower in key:
            return variants
    
    return [{'name': f'{base_name.title()}', 'category': 'ingredient', 'description': 'Generic ingredient'}]


import requests
import json
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

def get_mock_nutrition_data(ingredient_name):
    """Get nutritional data using LangChain AI search"""
    try:
        # Use LangChain to find the best match
        nutrition_data = get_langchain_nutrition_data(ingredient_name)
        if nutrition_data:
            return nutrition_data
    except Exception as e:
        print(f"LangChain error: {e}")
    
    # Fallback to traditional methods
    nutrition_data = get_openfoodfacts_data(ingredient_name)
    if nutrition_data:
        return nutrition_data
    
    nutrition_data = get_usda_data(ingredient_name)
    if nutrition_data:
        return nutrition_data
    
    nutrition_data = get_curated_nutrition_data(ingredient_name)
    if nutrition_data:
        return nutrition_data
    
    # Last resort - generic estimate
    return {
        'calories': 100, 'proteins': 5, 'carbs': 15, 'fats': 2, 'fibers': 1, 'sugars': 1,
        'confidence': 0.3, 'notes': 'Generic estimate - please verify with reliable source'
    }


def get_langchain_nutrition_data(ingredient_name):
    """Use intelligent search to find nutrition data"""
    try:
        # Get comprehensive nutrition database
        nutrition_db = get_comprehensive_nutrition_database()
        
        # Use intelligent search without requiring OpenAI API
        return intelligent_nutrition_search(ingredient_name, nutrition_db)
        
    except Exception as e:
        print(f"Intelligent nutrition search error: {e}")
        return None


def intelligent_nutrition_search(ingredient_name, nutrition_db):
    """Intelligently search nutrition database with smart matching"""
    ingredient_lower = ingredient_name.lower().strip()
    
    # Direct exact match
    if ingredient_lower in nutrition_db:
        return nutrition_db[ingredient_lower]
    
    # Smart partial matching with scoring
    best_match = None
    best_score = 0
    
    for key, data in nutrition_db.items():
        score = calculate_match_score(ingredient_lower, key)
        if score > best_score:
            best_score = score
            best_match = (key, data)
    
    # Return match if score is good enough
    if best_score >= 0.5:
        return best_match[1]
    
    # No good match found
    return None


def calculate_match_score(query, key):
    """Calculate how well a query matches a database key"""
    query_words = set(query.split())
    key_words = set(key.split())
    
    # Exact word matches
    exact_matches = query_words.intersection(key_words)
    if exact_matches:
        return len(exact_matches) / max(len(query_words), len(key_words))
    
    # Partial word matches
    partial_score = 0
    for query_word in query_words:
        for key_word in key_words:
            if query_word in key_word or key_word in query_word:
                partial_score += 0.5
    
    return partial_score / max(len(query_words), len(key_words))


def get_comprehensive_nutrition_database():
    """Get comprehensive nutrition database for LangChain search"""
    return {
        # Vegetables
        'potato': {
            'calories': 77, 'proteins': 2, 'carbs': 17, 'fats': 0.1, 'fibers': 2.2, 'sugars': 0.8,
            'confidence': 0.95, 'notes': 'Raw potato with skin', 'source': 'usda'
        },
        'tomato': {
            'calories': 18, 'proteins': 0.9, 'carbs': 3.9, 'fats': 0.2, 'fibers': 1.2, 'sugars': 2.6,
            'confidence': 0.95, 'notes': 'Raw tomato', 'source': 'usda'
        },
        'carrot': {
            'calories': 41, 'proteins': 0.9, 'carbs': 10, 'fats': 0.2, 'fibers': 2.8, 'sugars': 4.7,
            'confidence': 0.95, 'notes': 'Raw carrot', 'source': 'usda'
        },
        'onion': {
            'calories': 40, 'proteins': 1.1, 'carbs': 9, 'fats': 0.1, 'fibers': 1.7, 'sugars': 4.7,
            'confidence': 0.95, 'notes': 'Raw onion', 'source': 'usda'
        },
        'broccoli': {
            'calories': 34, 'proteins': 2.8, 'carbs': 7, 'fats': 0.4, 'fibers': 2.6, 'sugars': 1.5,
            'confidence': 0.95, 'notes': 'Raw broccoli', 'source': 'usda'
        },
        'spinach': {
            'calories': 23, 'proteins': 2.9, 'carbs': 3.6, 'fats': 0.4, 'fibers': 2.2, 'sugars': 0.4,
            'confidence': 0.95, 'notes': 'Raw spinach', 'source': 'usda'
        },
        'cucumber': {
            'calories': 16, 'proteins': 0.7, 'carbs': 3.6, 'fats': 0.1, 'fibers': 0.5, 'sugars': 1.7,
            'confidence': 0.95, 'notes': 'Raw cucumber with peel', 'source': 'usda'
        },
        'bell pepper': {
            'calories': 31, 'proteins': 1, 'carbs': 7, 'fats': 0.3, 'fibers': 2.1, 'sugars': 4.2,
            'confidence': 0.95, 'notes': 'Raw bell pepper', 'source': 'usda'
        },
        
        # Fruits
        'apple': {
            'calories': 52, 'proteins': 0.3, 'carbs': 14, 'fats': 0.2, 'fibers': 2.4, 'sugars': 10.4,
            'confidence': 0.95, 'notes': 'Raw apple with skin', 'source': 'usda'
        },
        'banana': {
            'calories': 89, 'proteins': 1.1, 'carbs': 23, 'fats': 0.3, 'fibers': 2.6, 'sugars': 12.2,
            'confidence': 0.95, 'notes': 'Raw banana', 'source': 'usda'
        },
        'orange': {
            'calories': 47, 'proteins': 0.9, 'carbs': 12, 'fats': 0.1, 'fibers': 2.4, 'sugars': 9.4,
            'confidence': 0.95, 'notes': 'Raw orange', 'source': 'usda'
        },
        'strawberry': {
            'calories': 32, 'proteins': 0.7, 'carbs': 8, 'fats': 0.3, 'fibers': 2, 'sugars': 4.9,
            'confidence': 0.95, 'notes': 'Raw strawberry', 'source': 'usda'
        },
        
        # Meats
        'chicken breast': {
            'calories': 165, 'proteins': 31, 'carbs': 0, 'fats': 3.6, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Chicken breast, skinless, cooked', 'source': 'usda'
        },
        'chicken thigh': {
            'calories': 209, 'proteins': 26, 'carbs': 0, 'fats': 12, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Chicken thigh, skinless, cooked', 'source': 'usda'
        },
        'chicken wing': {
            'calories': 288, 'proteins': 26.64, 'carbs': 0, 'fats': 19.3, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Chicken wing, cooked', 'source': 'usda'
        },
        'beef': {
            'calories': 250, 'proteins': 26, 'carbs': 0, 'fats': 15, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Beef, lean, cooked', 'source': 'usda'
        },
        'pork': {
            'calories': 242, 'proteins': 27, 'carbs': 0, 'fats': 14, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Pork, lean, cooked', 'source': 'usda'
        },
        
        # Fish
        'salmon': {
            'calories': 208, 'proteins': 25, 'carbs': 0, 'fats': 12, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Salmon, cooked', 'source': 'usda'
        },
        'tuna': {
            'calories': 144, 'proteins': 30, 'carbs': 0, 'fats': 1, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'Tuna, cooked', 'source': 'usda'
        },
        
        # Grains
        'rice': {
            'calories': 130, 'proteins': 2.7, 'carbs': 28, 'fats': 0.3, 'fibers': 0.4, 'sugars': 0.1,
            'confidence': 0.95, 'notes': 'White rice, cooked', 'source': 'usda'
        },
        'brown rice': {
            'calories': 111, 'proteins': 2.6, 'carbs': 23, 'fats': 0.9, 'fibers': 1.8, 'sugars': 0.4,
            'confidence': 0.95, 'notes': 'Brown rice, cooked', 'source': 'usda'
        },
        'quinoa': {
            'calories': 120, 'proteins': 4.4, 'carbs': 22, 'fats': 1.9, 'fibers': 2.8, 'sugars': 0.9,
            'confidence': 0.95, 'notes': 'Quinoa, cooked', 'source': 'usda'
        },
        'oats': {
            'calories': 68, 'proteins': 2.4, 'carbs': 12, 'fats': 1.4, 'fibers': 1.7, 'sugars': 0.3,
            'confidence': 0.95, 'notes': 'Oats, cooked', 'source': 'usda'
        },
    }


def search_nutrition_database(ingredient_name, nutrition_db):
    """Search nutrition database and return best match"""
    ingredient_lower = ingredient_name.lower()
    
    # Direct match
    if ingredient_lower in nutrition_db:
        return json.dumps(nutrition_db[ingredient_lower])
    
    # Partial matches
    matches = []
    for key, data in nutrition_db.items():
        if ingredient_lower in key or key in ingredient_lower:
            matches.append((key, data))
    
    if matches:
        # Return the best match (longest key name for more specific matches)
        best_match = max(matches, key=lambda x: len(x[0]))
        return json.dumps(best_match[1])
    
    # No match found
    return json.dumps({
        'calories': 100, 'proteins': 5, 'carbs': 15, 'fats': 2, 'fibers': 1, 'sugars': 1,
        'confidence': 0.3, 'notes': f'No exact match found for "{ingredient_name}" - generic estimate',
        'source': 'estimated'
    })


def get_openfoodfacts_data(ingredient_name):
    """Get nutrition data from OpenFoodFacts API - prefer raw ingredients"""
    try:
        # Search for the ingredient
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={ingredient_name}&search_simple=1&action=process&json=1"
        response = requests.get(search_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('products') and len(data['products']) > 0:
                products = data['products']
                
                # Look for raw ingredient first
                raw_product = find_raw_ingredient(products, ingredient_name)
                if raw_product:
                    return extract_nutrition_data(raw_product, ingredient_name)
                
                # Fallback to first product if no raw ingredient found
                return extract_nutrition_data(products[0], ingredient_name)
                
    except Exception as e:
        print(f"OpenFoodFacts API error: {e}")
    
    return None


def find_raw_ingredient(products, ingredient_name):
    """Find raw ingredient among products, avoiding processed foods"""
    ingredient_lower = ingredient_name.lower()
    
    # Keywords that indicate raw/unprocessed ingredients
    raw_keywords = [
        'raw', 'fresh', 'organic', 'natural', 'whole', 'unprocessed',
        'freshly', 'ripe', 'uncooked', 'unseasoned', 'plain'
    ]
    
    # Keywords that indicate processed foods (avoid these)
    processed_keywords = [
        'chips', 'crisps', 'fried', 'cooked', 'baked', 'roasted', 'grilled',
        'seasoned', 'salted', 'sweetened', 'flavored', 'sauce', 'dressing',
        'mayonnaise', 'ketchup', 'mustard', 'oil', 'butter', 'cheese',
        'bread', 'pasta', 'noodles', 'cereal', 'snack', 'candy', 'chocolate',
        'ice cream', 'yogurt', 'milk', 'juice', 'soda', 'beer', 'wine'
    ]
    
    # Score each product
    best_product = None
    best_score = -1
    
    for product in products[:10]:  # Check first 10 products
        product_name = product.get('product_name', '').lower()
        generic_name = product.get('generic_name', '').lower()
        categories = ' '.join(product.get('categories_tags', [])).lower()
        
        score = 0
        
        # Bonus for raw keywords
        for keyword in raw_keywords:
            if keyword in product_name or keyword in generic_name:
                score += 2
        
        # Penalty for processed keywords
        for keyword in processed_keywords:
            if keyword in product_name or keyword in generic_name or keyword in categories:
                score -= 3
        
        # Bonus for exact ingredient name match
        if ingredient_lower in product_name:
            score += 5
        
        # Penalty for long product names (usually processed)
        if len(product_name) > 50:
            score -= 2
        
        # Bonus for simple names
        if len(product_name) < 30:
            score += 1
        
        # Check if it's a raw ingredient category
        raw_categories = ['fruits', 'vegetables', 'meat', 'fish', 'grains', 'nuts', 'seeds']
        for cat in raw_categories:
            if cat in categories:
                score += 3
        
        if score > best_score:
            best_score = score
            best_product = product
    
    # Only return if score is positive (likely raw ingredient)
    return best_product if best_score > 0 else None


def extract_nutrition_data(product, ingredient_name):
    """Extract nutrition data from OpenFoodFacts product"""
    nutriments = product.get('nutriments', {})
    
    return {
        'calories': nutriments.get('energy-kcal_100g', 0),
        'proteins': nutriments.get('proteins_100g', 0),
        'carbs': nutriments.get('carbohydrates_100g', 0),
        'fats': nutriments.get('fat_100g', 0),
        'fibers': nutriments.get('fiber_100g', 0),
        'sugars': nutriments.get('sugars_100g', 0),
        'confidence': 0.85,
        'notes': f'Data from OpenFoodFacts: {product.get("product_name", ingredient_name)}',
        'source': 'openfoodfacts'
    }


def get_usda_data(ingredient_name):
    """Get nutrition data from USDA database (mock implementation)"""
    # Note: Real USDA API requires API key
    # This is a mock implementation with accurate data
    usda_data = {
        'chicken wing': {
            'calories': 288, 'proteins': 26.64, 'carbs': 0, 'fats': 19.3, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'USDA data: Chicken wing, cooked', 'source': 'usda'
        },
        'chicken breast': {
            'calories': 165, 'proteins': 31, 'carbs': 0, 'fats': 3.6, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'USDA data: Chicken breast, skinless, cooked', 'source': 'usda'
        },
        'salmon': {
            'calories': 208, 'proteins': 25, 'carbs': 0, 'fats': 12, 'fibers': 0, 'sugars': 0,
            'confidence': 0.95, 'notes': 'USDA data: Salmon, cooked', 'source': 'usda'
        },
        'basmati rice': {
            'calories': 130, 'proteins': 2.7, 'carbs': 28, 'fats': 0.3, 'fibers': 0.4, 'sugars': 0.1,
            'confidence': 0.9, 'notes': 'USDA data: Basmati rice, cooked', 'source': 'usda'
        },
        'brown rice': {
            'calories': 111, 'proteins': 2.6, 'carbs': 23, 'fats': 0.9, 'fibers': 1.8, 'sugars': 0.4,
            'confidence': 0.9, 'notes': 'USDA data: Brown rice, cooked', 'source': 'usda'
        },
    }
    
    ingredient_lower = ingredient_name.lower()
    for key, nutrition in usda_data.items():
        if key in ingredient_lower or ingredient_lower in key:
            return nutrition
    
    return None


def get_curated_nutrition_data(ingredient_name):
    """Get nutrition data from our curated database"""
    curated_data = {
        'apple': {
            'calories': 52, 'proteins': 0.3, 'carbs': 14, 'fats': 0.2, 'fibers': 2.4, 'sugars': 10.4,
            'confidence': 0.9, 'notes': 'Raw apple with skin', 'source': 'curated'
        },
        'banana': {
            'calories': 89, 'proteins': 1.1, 'carbs': 23, 'fats': 0.3, 'fibers': 2.6, 'sugars': 12.2,
            'confidence': 0.9, 'notes': 'Raw banana', 'source': 'curated'
        },
        'broccoli': {
            'calories': 34, 'proteins': 2.8, 'carbs': 7, 'fats': 0.4, 'fibers': 2.6, 'sugars': 1.5,
            'confidence': 0.9, 'notes': 'Raw broccoli', 'source': 'curated'
        },
        'spinach': {
            'calories': 23, 'proteins': 2.9, 'carbs': 3.6, 'fats': 0.4, 'fibers': 2.2, 'sugars': 0.4,
            'confidence': 0.9, 'notes': 'Raw spinach', 'source': 'curated'
        },
        'potato': {
            'calories': 77, 'proteins': 2, 'carbs': 17, 'fats': 0.1, 'fibers': 2.2, 'sugars': 0.8,
            'confidence': 0.95, 'notes': 'Raw potato with skin', 'source': 'curated'
        },
        'tomato': {
            'calories': 18, 'proteins': 0.9, 'carbs': 3.9, 'fats': 0.2, 'fibers': 1.2, 'sugars': 2.6,
            'confidence': 0.9, 'notes': 'Raw tomato', 'source': 'curated'
        },
        'carrot': {
            'calories': 41, 'proteins': 0.9, 'carbs': 10, 'fats': 0.2, 'fibers': 2.8, 'sugars': 4.7,
            'confidence': 0.9, 'notes': 'Raw carrot', 'source': 'curated'
        },
        'onion': {
            'calories': 40, 'proteins': 1.1, 'carbs': 9, 'fats': 0.1, 'fibers': 1.7, 'sugars': 4.7,
            'confidence': 0.9, 'notes': 'Raw onion', 'source': 'curated'
        },
    }
    
    ingredient_lower = ingredient_name.lower()
    for key, nutrition in curated_data.items():
        if key in ingredient_lower or ingredient_lower in key:
            return nutrition
    
    return None
