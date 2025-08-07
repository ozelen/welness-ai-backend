from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import (
    Diet, Meal, Category, Ingredient, MealIngredient, 
    MealRecord, MealPreference
)
from goals.models import Goal


class MealPreferenceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Vegetables')
        self.ingredient = Ingredient.objects.create(
            name='Carrot',
            category=self.category,
            proteins=0.9,
            fats=0.2,
            carbs=9.6,
            calories=41,
            fibers=2.8,
            sugars=4.7
        )

    def test_meal_preference_creation(self):
        preference = MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='love',
            description='I love carrots!'
        )
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.ingredient, self.ingredient)
        self.assertEqual(preference.preference_type, 'love')
        self.assertEqual(preference.description, 'I love carrots!')

    def test_meal_preference_str_representation(self):
        preference = MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='dislike'
        )
        expected_str = f"{self.user} dislike {self.ingredient.name}"
        self.assertEqual(str(preference), expected_str)


class MealPreferenceAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Fruits')
        self.ingredient = Ingredient.objects.create(
            name='Apple',
            category=self.category,
            proteins=0.3,
            fats=0.2,
            carbs=14,
            calories=52,
            fibers=2.4,
            sugars=10.4
        )
        self.client.force_authenticate(user=self.user)

    def test_create_meal_preference(self):
        url = reverse('meals:meal-preference-list')
        data = {
            'ingredient_id': self.ingredient.id,
            'preference_type': 'like',
            'description': 'I like apples'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MealPreference.objects.count(), 1)
        preference = MealPreference.objects.first()
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.ingredient, self.ingredient)
        self.assertEqual(preference.preference_type, 'like')

    def test_create_meal_preference_with_new_ingredient(self):
        url = reverse('meals:meal-preference-list')
        data = {
            'ingredient_name': 'Banana',
            'preference_type': 'love',
            'description': 'I love bananas!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MealPreference.objects.count(), 1)
        self.assertEqual(Ingredient.objects.filter(name='Banana').count(), 1)

    def test_list_meal_preferences(self):
        MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='like'
        )
        url = reverse('meals:meal-preference-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_meal_preference_detail(self):
        preference = MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='dislike'
        )
        url = reverse('meals:meal-preference-detail', args=[preference.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['preference_type'], 'dislike')

    def test_update_meal_preference(self):
        preference = MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='like'
        )
        url = reverse('meals:meal-preference-detail', args=[preference.id])
        data = {
            'preference_type': 'love',
            'description': 'Actually, I love it!'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        preference.refresh_from_db()
        self.assertEqual(preference.preference_type, 'love')
        self.assertEqual(preference.description, 'Actually, I love it!')

    def test_delete_meal_preference(self):
        preference = MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='like'
        )
        url = reverse('meals:delete-meal-preference', args=[preference.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MealPreference.objects.count(), 0)

    def test_get_meal_preferences_by_type(self):
        MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='love'
        )
        url = reverse('meals:meal-preference-by-type', args=['love'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_meal_preferences_summary(self):
        MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='love'
        )
        url = reverse('meals:meal-preference-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_preferences'], 1)
        self.assertEqual(response.data['by_type']['love'], 1)

    def test_bulk_update_meal_preferences(self):
        preference = MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='like'
        )
        url = reverse('meals:bulk-update-preferences')
        data = {
            'preferences': [
                {
                    'id': preference.id,
                    'preference_type': 'love',
                    'description': 'Updated description'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        preference.refresh_from_db()
        self.assertEqual(preference.preference_type, 'love')
        self.assertEqual(preference.description, 'Updated description')

    def test_ingredient_search(self):
        url = reverse('meals:ingredient-search')
        response = self.client.get(url, {'q': 'apple'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_ingredient_suggestions(self):
        MealPreference.objects.create(
            user=self.user,
            ingredient=self.ingredient,
            preference_type='like'
        )
        url = reverse('meals:ingredient-suggestions')
        response = self.client.get(url, {'q': 'apple'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not suggest ingredients user already has preferences for
        self.assertEqual(len(response.data['suggestions']), 0)


class MealPreferenceUnauthorizedTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Fruits')
        self.ingredient = Ingredient.objects.create(
            name='Apple',
            category=self.category,
            proteins=0.3,
            fats=0.2,
            carbs=14,
            calories=52,
            fibers=2.4,
            sugars=10.4
        )

    def test_unauthorized_access(self):
        url = reverse('meals:meal-preference-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_create(self):
        url = reverse('meals:meal-preference-list')
        data = {
            'ingredient_id': self.ingredient.id,
            'preference_type': 'like'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
