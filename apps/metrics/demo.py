#!/usr/bin/env python3
"""
Demo script for the Health Calculator using data from Google Spreadsheet
"""

import os
import sys
import django
from datetime import date

# Add the parent directory to the path so we can import Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')
django.setup()

from django.contrib.auth.models import User
from user_auth.models import UserProfile
from metrics.models import HealthCalculator, BodyMeasurement
from metrics.services import HealthCalculatorService


def demo_health_calculator():
    """Demonstrate the health calculator with Google Spreadsheet data"""
    
    print("🏥 Health Calculator Demo")
    print("=" * 50)
    
    # Data from your Google Spreadsheet
    spreadsheet_data = {
        'weight_kg': 97,
        'height_cm': 192,
        'age_years': 41,  # From your spreadsheet
        'body_fat_percentage': 20,
        'gender': 'male'
    }
    
    print(f"📊 Input Data:")
    print(f"   Weight: {spreadsheet_data['weight_kg']} kg")
    print(f"   Height: {spreadsheet_data['height_cm']} cm")
    print(f"   Age: {spreadsheet_data['age_years']} years")
    print(f"   Body Fat: {spreadsheet_data['body_fat_percentage']}%")
    print(f"   Gender: {spreadsheet_data['gender']}")
    print()
    
    # Calculate LBM using the service (same as your Google Spreadsheet formula)
    lbm = HealthCalculatorService.calculate_lbm(
        spreadsheet_data['weight_kg'], 
        spreadsheet_data['body_fat_percentage']
    )
    
    print(f"💪 Lean Body Mass (LBM) Calculation:")
    print(f"   Formula: LBM = Weight × (1 - Body Fat % / 100)")
    print(f"   LBM = {spreadsheet_data['weight_kg']} × (1 - {spreadsheet_data['body_fat_percentage']} / 100)")
    print(f"   LBM = {spreadsheet_data['weight_kg']} × {1 - spreadsheet_data['body_fat_percentage'] / 100}")
    print(f"   LBM = {lbm:.1f} kg")
    print()
    
    # Calculate BMR
    bmr = HealthCalculatorService.calculate_bmr(
        spreadsheet_data['weight_kg'],
        spreadsheet_data['height_cm'],
        spreadsheet_data['age_years'],
        spreadsheet_data['gender']
    )
    
    print(f"🔥 Basal Metabolic Rate (BMR) Calculation:")
    print(f"   Formula (Mifflin-St Jeor):")
    if spreadsheet_data['gender'] == 'male':
        print(f"   BMR = 10 × weight + 6.25 × height - 5 × age + 5")
        print(f"   BMR = 10 × {spreadsheet_data['weight_kg']} + 6.25 × {spreadsheet_data['height_cm']} - 5 × {spreadsheet_data['age_years']} + 5")
    else:
        print(f"   BMR = 10 × weight + 6.25 × height - 5 × age - 161")
        print(f"   BMR = 10 × {spreadsheet_data['weight_kg']} + 6.25 × {spreadsheet_data['height_cm']} - 5 × {spreadsheet_data['age_years']} - 161")
    
    print(f"   BMR = {bmr:.0f} kcal/day")
    print()
    
    # Calculate TDEE for different activity levels
    activity_levels = {
        'sedentary': 'Sedentary (little or no exercise)',
        'lightly_active': 'Lightly Active (light exercise 1-3 days/week)',
        'moderately_active': 'Moderately Active (moderate exercise 3-5 days/week)',
        'very_active': 'Very Active (hard exercise 6-7 days/week)',
        'extremely_active': 'Extremely Active (very hard exercise, physical job)'
    }
    
    print(f"⚡ Total Daily Energy Expenditure (TDEE) Calculations:")
    print(f"   Base BMR: {bmr:.0f} kcal/day")
    print()
    
    for level, description in activity_levels.items():
        tdee = HealthCalculatorService.calculate_tdee(bmr, level)
        multiplier = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9,
        }[level]
        
        print(f"   {description}:")
        print(f"     Multiplier: {multiplier}")
        print(f"     TDEE: {tdee:.0f} kcal/day")
        print()
    
    # Calculate BMI
    bmi = HealthCalculatorService.calculate_bmi(
        spreadsheet_data['weight_kg'],
        spreadsheet_data['height_cm']
    )
    bmi_category = HealthCalculatorService.get_bmi_category(bmi)
    
    print(f"📏 Body Mass Index (BMI) Calculation:")
    print(f"   Formula: BMI = weight(kg) / height(m)²")
    height_m = spreadsheet_data['height_cm'] / 100
    print(f"   BMI = {spreadsheet_data['weight_kg']} / ({height_m})²")
    print(f"   BMI = {spreadsheet_data['weight_kg']} / {height_m ** 2:.2f}")
    print(f"   BMI = {bmi:.1f}")
    print(f"   Category: {bmi_category}")
    print()
    
    # Calculate body fat mass
    body_fat_mass = HealthCalculatorService.calculate_body_fat_mass(
        spreadsheet_data['weight_kg'],
        spreadsheet_data['body_fat_percentage']
    )
    
    print(f"🩸 Body Fat Mass Calculation:")
    print(f"   Formula: Body Fat Mass = Weight × (Body Fat % / 100)")
    print(f"   Body Fat Mass = {spreadsheet_data['weight_kg']} × ({spreadsheet_data['body_fat_percentage']} / 100)")
    print(f"   Body Fat Mass = {body_fat_mass:.1f} kg")
    print()
    
    print("✅ All calculations completed successfully!")
    print("\n💡 This matches your Google Spreadsheet formula:")
    print("   = IF(' БЖВ'!B5 > 0; ' БЖВ'!B2 * (1 - ' БЖВ'!B5 / 100); \"%\")")
    print(f"   Where B2 = {spreadsheet_data['weight_kg']} kg and B5 = {spreadsheet_data['body_fat_percentage']}%")


def demo_with_database():
    """Demonstrate creating and storing health calculations in the database"""
    
    print("\n🗄️ Database Integration Demo")
    print("=" * 50)
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    # Set up user profile with date of birth
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'date_of_birth': date(1983, 1, 1)}  # 41 years old
    )
    if not created:
        profile.date_of_birth = date(1983, 1, 1)
        profile.save()
    
    # Create body measurements
    measurements_data = [
        ('weight_kg', 97, 'kg'),
        ('height_cm', 192, 'cm'),
        ('body_fat_percentage', 20, '%'),
    ]
    
    for metric, value, unit in measurements_data:
        BodyMeasurement.objects.create(
            user=user,
            metric=metric,
            value=value,
            unit=unit,
            measurement_type='log'
        )
    
    print(f"✅ Created body measurements for user: {user.username}")
    
    # Create health calculator
    calculator = HealthCalculator.objects.create(
        user=user,
        weight_kg=97,
        height_cm=192,
        body_fat_percentage=20,
        gender='male',
        activity_level='moderately_active',
        activity_hours_per_week=5.0  # 1.38 + 1.93 hours from your spreadsheet
    )
    
    # Calculate all metrics
    results = calculator.calculate_all()
    
    print(f"✅ Created health calculator with ID: {calculator.id}")
    print(f"📊 Calculated Results:")
    print(f"   LBM: {results['lbm_kg']:.1f} kg")
    print(f"   BMR: {results['bmr_kcal']:.0f} kcal/day")
    print(f"   TDEE: {results['tdee_kcal']:.0f} kcal/day")
    print(f"   BMI: {results['bmi']:.1f}")
    print(f"   Body Fat Mass: {results['body_fat_mass_kg']:.1f} kg")
    
    # Show how to retrieve the data
    print(f"\n📥 Retrieving data from database:")
    latest_calculator = HealthCalculator.objects.filter(user=user).latest('calculation_date')
    print(f"   Latest calculation: {latest_calculator.calculation_date}")
    print(f"   Data as dict: {latest_calculator.to_dict()}")


if __name__ == '__main__':
    demo_health_calculator()
    demo_with_database()
