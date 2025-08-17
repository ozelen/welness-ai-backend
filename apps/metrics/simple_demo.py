#!/usr/bin/env python3
"""
Simple demo script for the Health Calculator using data from Google Spreadsheet
This version doesn't require Django setup
"""

def calculate_lbm(weight_kg, body_fat_percentage):
    """
    Calculate Lean Body Mass (LBM)
    Formula: LBM = Weight * (1 - Body Fat % / 100)
    """
    if body_fat_percentage > 0:
        return weight_kg * (1 - body_fat_percentage / 100)
    return None

def calculate_bmr(weight_kg, height_cm, age_years, gender):
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    """
    if gender == 'male':
        return 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
    else:  # female
        return 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure (TDEE)
    """
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extremely_active': 1.9,
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    return bmr * multiplier

def calculate_bmi(weight_kg, height_cm):
    """
    Calculate Body Mass Index (BMI)
    """
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def get_bmi_category(bmi):
    """
    Get BMI category based on BMI value
    """
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal weight'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def calculate_body_fat_mass(weight_kg, body_fat_percentage):
    """
    Calculate body fat mass
    """
    return weight_kg * (body_fat_percentage / 100)


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
    lbm = calculate_lbm(
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
    bmr = calculate_bmr(
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
        tdee = calculate_tdee(bmr, level)
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
    bmi = calculate_bmi(
        spreadsheet_data['weight_kg'],
        spreadsheet_data['height_cm']
    )
    bmi_category = get_bmi_category(bmi)
    
    print(f"📏 Body Mass Index (BMI) Calculation:")
    print(f"   Formula: BMI = weight(kg) / height(m)²")
    height_m = spreadsheet_data['height_cm'] / 100
    print(f"   BMI = {spreadsheet_data['weight_kg']} / ({height_m})²")
    print(f"   BMI = {spreadsheet_data['weight_kg']} / {height_m ** 2:.2f}")
    print(f"   BMI = {bmi:.1f}")
    print(f"   Category: {bmi_category}")
    print()
    
    # Calculate body fat mass
    body_fat_mass = calculate_body_fat_mass(
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
    
    print("\n📋 Summary:")
    print(f"   • Lean Body Mass: {lbm:.1f} kg")
    print(f"   • Basal Metabolic Rate: {bmr:.0f} kcal/day")
    print(f"   • TDEE (Moderate Activity): {calculate_tdee(bmr, 'moderately_active'):.0f} kcal/day")
    print(f"   • BMI: {bmi:.1f} ({bmi_category})")
    print(f"   • Body Fat Mass: {body_fat_mass:.1f} kg")


if __name__ == '__main__':
    demo_health_calculator()
