from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from .models import HealthCalculator, BodyMeasurement
from .services import HealthCalculatorService


class HealthCalculatorTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Set date of birth in user profile
        from user_auth.models import UserProfile
        self.profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={'date_of_birth': date(1985, 6, 15)}  # 39 years old in 2024
        )
        if not created:
            self.profile.date_of_birth = date(1985, 6, 15)
            self.profile.save()

    def test_lbm_calculation(self):
        """Test Lean Body Mass calculation"""
        # Test data from your Google Spreadsheet
        weight_kg = 97
        body_fat_percentage = 20
        
        # Calculate LBM using the service
        lbm = HealthCalculatorService.calculate_lbm(weight_kg, body_fat_percentage)
        
        # Expected result: 97 * (1 - 20/100) = 97 * 0.8 = 77.6
        expected_lbm = 77.6
        
        self.assertAlmostEqual(lbm, expected_lbm, places=1)
    
    def test_lbm_calculation_zero_body_fat(self):
        """Test LBM calculation with zero body fat"""
        weight_kg = 97
        body_fat_percentage = 0
        
        lbm = HealthCalculatorService.calculate_lbm(weight_kg, body_fat_percentage)
        
        # Should return None when body fat is 0
        self.assertIsNone(lbm)
    
    def test_bmr_calculation_male(self):
        """Test BMR calculation for male"""
        weight_kg = 97
        height_cm = 192
        age_years = 39
        gender = 'male'
        
        bmr = HealthCalculatorService.calculate_bmr(weight_kg, height_cm, age_years, gender)
        
        # Expected: 10 × 97 + 6.25 × 192 - 5 × 39 + 5 = 970 + 1200 - 195 + 5 = 1980
        expected_bmr = 1980
        
        self.assertAlmostEqual(bmr, expected_bmr, places=0)
    
    def test_bmr_calculation_female(self):
        """Test BMR calculation for female"""
        weight_kg = 70
        height_cm = 165
        age_years = 30
        gender = 'female'
        
        bmr = HealthCalculatorService.calculate_bmr(weight_kg, height_cm, age_years, gender)
        
        # Expected: 10 × 70 + 6.25 × 165 - 5 × 30 - 161 = 700 + 1031.25 - 150 - 161 = 1420.25
        expected_bmr = 1420.25
        
        self.assertAlmostEqual(bmr, expected_bmr, places=0)
    
    def test_tdee_calculation(self):
        """Test TDEE calculation"""
        bmr = 1980
        activity_level = 'moderately_active'
        
        tdee = HealthCalculatorService.calculate_tdee(bmr, activity_level)
        
        # Expected: 1980 × 1.55 = 3069
        expected_tdee = 3069
        
        self.assertAlmostEqual(tdee, expected_tdee, places=0)
    
    def test_bmi_calculation(self):
        """Test BMI calculation"""
        weight_kg = 97
        height_cm = 192
        
        bmi = HealthCalculatorService.calculate_bmi(weight_kg, height_cm)
        
        # Expected: 97 / (1.92)² = 97 / 3.6864 = 26.3
        expected_bmi = 26.3
        
        self.assertAlmostEqual(bmi, expected_bmi, places=1)
    
    def test_health_calculator_model(self):
        """Test the HealthCalculator model"""
        calculator = HealthCalculator.objects.create(
            user=self.user,
            weight_kg=97,
            height_cm=192,
            body_fat_percentage=20,
            gender='male',
            activity_level='moderately_active'
        )
        
        # Calculate all metrics
        results = calculator.calculate_all()
        
        # Verify LBM calculation
        self.assertAlmostEqual(results['lbm_kg'], 77.6, places=1)
        
        # Verify BMI calculation
        self.assertAlmostEqual(results['bmi'], 26.3, places=1)
        
        # Verify body fat mass calculation
        self.assertAlmostEqual(results['body_fat_mass_kg'], 19.4, places=1)
        
        # BMR and TDEE depend on age, so we'll test them separately
        age = calculator.get_age()
        if age is not None:
            # Verify BMR calculation
            self.assertAlmostEqual(results['bmr_kcal'], 1980, places=0)
            
            # Verify TDEE calculation
            self.assertAlmostEqual(results['tdee_kcal'], 3069, places=0)
        else:
            # If age is None, BMR and TDEE should also be None
            self.assertIsNone(results['bmr_kcal'])
            self.assertIsNone(results['tdee_kcal'])
    
    def test_age_calculation_from_profile(self):
        """Test age calculation from user profile"""
        calculator = HealthCalculator.objects.create(
            user=self.user,
            weight_kg=97,
            height_cm=192,
            body_fat_percentage=20,
            gender='male',
            activity_level='moderately_active'
        )
        
        age = calculator.get_age()
        
        # Should calculate age from date of birth
        self.assertIsNotNone(age)
        self.assertGreater(age, 0)
    
    def test_body_measurement_model(self):
        """Test BodyMeasurement model"""
        measurement = BodyMeasurement.objects.create(
            user=self.user,
            metric='weight_kg',
            value=97,
            unit='kg',
            measurement_type='log'
        )
        
        self.assertEqual(measurement.value, 97)
        self.assertEqual(measurement.unit, 'kg')
        self.assertEqual(measurement.metric, 'weight_kg')
        self.assertEqual(measurement.get_metric_display(), 'Weight (kg)')
