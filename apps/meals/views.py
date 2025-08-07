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
