from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from metrics.models import Metric


class Command(BaseCommand):
    help = 'Populate the database with common health metrics'

    def handle(self, *args, **options):
        self.stdout.write('Creating common health metrics...')
        
        # Body measurements
        body_metrics = [
            {
                'metric_id': 'WEIGHT',
                'name': 'Weight',
                'type': 'body_measurement',
                'unit': 'kg',
                'description': 'Body weight in kilograms',
                'min_value': 20,
                'max_value': 300,
                'icon': 'fas fa-weight',
                'color': '#667eea'
            },
            {
                'metric_id': 'HEIGHT',
                'name': 'Height',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Height in centimeters',
                'min_value': 100,
                'max_value': 250,
                'icon': 'fas fa-ruler-vertical',
                'color': '#764ba2'
            },
            {
                'metric_id': 'BF_PCT',
                'name': 'Body Fat Percentage',
                'type': 'body_measurement',
                'unit': '%',
                'description': 'Body fat percentage',
                'min_value': 0,
                'max_value': 50,
                'icon': 'fas fa-percentage',
                'color': '#f093fb'
            },
            {
                'metric_id': 'WAIST_CIRC',
                'name': 'Waist Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Waist circumference measurement',
                'min_value': 50,
                'max_value': 200,
                'icon': 'fas fa-circle',
                'color': '#43e97b'
            },
            {
                'metric_id': 'HIP_CIRC',
                'name': 'Hip Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Hip circumference measurement',
                'min_value': 60,
                'max_value': 200,
                'icon': 'fas fa-circle',
                'color': '#38f9d7'
            },
            {
                'metric_id': 'CHEST_CIRC',
                'name': 'Chest Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Chest circumference measurement',
                'min_value': 60,
                'max_value': 200,
                'icon': 'fas fa-circle',
                'color': '#fa709a'
            },
            {
                'metric_id': 'NECK_CIRC',
                'name': 'Neck Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Neck circumference measurement',
                'min_value': 20,
                'max_value': 60,
                'icon': 'fas fa-circle',
                'color': '#a8edea'
            },
            {
                'metric_id': 'ARM_CIRC',
                'name': 'Arm Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Upper arm circumference measurement',
                'min_value': 15,
                'max_value': 80,
                'icon': 'fas fa-circle',
                'color': '#ffecd2'
            },
            {
                'metric_id': 'THIGH_CIRC',
                'name': 'Thigh Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Thigh circumference measurement',
                'min_value': 30,
                'max_value': 100,
                'icon': 'fas fa-circle',
                'color': '#fcb69f'
            },
            {
                'metric_id': 'CALF_CIRC',
                'name': 'Calf Circumference',
                'type': 'body_measurement',
                'unit': 'cm',
                'description': 'Calf circumference measurement',
                'min_value': 20,
                'max_value': 60,
                'icon': 'fas fa-circle',
                'color': '#ff9a9e'
            },
            {
                'metric_id': 'MUSCLE_PCT',
                'name': 'Muscle Mass Percentage',
                'type': 'body_measurement',
                'unit': '%',
                'description': 'Muscle mass percentage',
                'min_value': 20,
                'max_value': 80,
                'icon': 'fas fa-dumbbell',
                'color': '#a8edea'
            },
            {
                'metric_id': 'BW_PCT',
                'name': 'Body Water Percentage',
                'type': 'body_measurement',
                'unit': '%',
                'description': 'Body water percentage',
                'min_value': 30,
                'max_value': 80,
                'icon': 'fas fa-tint',
                'color': '#667eea'
            },
            {
                'metric_id': 'BONE_MASS',
                'name': 'Bone Mass',
                'type': 'body_measurement',
                'unit': 'kg',
                'description': 'Bone mass in kilograms',
                'min_value': 1,
                'max_value': 20,
                'icon': 'fas fa-bone',
                'color': '#f093fb'
            },
        ]

        # Calculated metrics (LBM, BMR, TDEE, BMI, Body Fat Mass)
        calculated_metrics = [
            {
                'metric_id': 'BMI',
                'name': 'BMI',
                'type': 'calculated',
                'unit': '',
                'description': 'Body Mass Index - calculated from weight and height',
                'is_calculated': True,
                'calculation_formula': 'WEIGHT / ((HEIGHT / 100) ** 2)',
                'min_value': 10,
                'max_value': 60,
                'icon': 'fas fa-chart-line',
                'color': '#4facfe'
            },
            {
                'metric_id': 'LBM',
                'name': 'Lean Body Mass',
                'type': 'calculated',
                'unit': 'kg',
                'description': 'Lean Body Mass - calculated from weight and body fat percentage',
                'is_calculated': True,
                'calculation_formula': 'WEIGHT * (1 - BF_PCT / 100)',
                'min_value': 20,
                'max_value': 200,
                'icon': 'fas fa-weight',
                'color': '#667eea'
            },
            {
                'metric_id': 'BF_MASS',
                'name': 'Body Fat Mass',
                'type': 'calculated',
                'unit': 'kg',
                'description': 'Body Fat Mass - calculated from weight and body fat percentage',
                'is_calculated': True,
                'calculation_formula': 'WEIGHT * (BF_PCT / 100)',
                'min_value': 0,
                'max_value': 100,
                'icon': 'fas fa-percentage',
                'color': '#f093fb'
            },
            {
                'metric_id': 'BMR',
                'name': 'Basal Metabolic Rate',
                'type': 'calculated',
                'unit': 'kcal/day',
                'description': 'Basal Metabolic Rate - calculated using Mifflin-St Jeor equation',
                'is_calculated': True,
                'calculation_formula': '10 * WEIGHT + 6.25 * HEIGHT - 5 * AGE + (5 if GENDER == "male" else -161)',
                'min_value': 800,
                'max_value': 4000,
                'icon': 'fas fa-fire',
                'color': '#ffa726'
            },
            {
                'metric_id': 'TDEE',
                'name': 'Total Daily Energy Expenditure',
                'type': 'calculated',
                'unit': 'kcal/day',
                'description': 'Total Daily Energy Expenditure - calculated from BMR and activity level',
                'is_calculated': True,
                'calculation_formula': 'BMR * ACTIVITY_MULTIPLIER',
                'min_value': 1000,
                'max_value': 8000,
                'icon': 'fas fa-chart-line',
                'color': '#4ecdc4'
            },
        ]

        # Lab results
        lab_metrics = [
            {
                'metric_id': 'GLUCOSE',
                'name': 'Blood Glucose',
                'type': 'lab_result',
                'unit': 'mg/dL',
                'description': 'Blood glucose level',
                'reference_range': '70-100',
                'min_value': 20,
                'max_value': 600,
                'icon': 'fas fa-tint',
                'color': '#ff6b6b'
            },
            {
                'metric_id': 'HBA1C',
                'name': 'Hemoglobin A1c',
                'type': 'lab_result',
                'unit': '%',
                'description': 'Glycated hemoglobin',
                'reference_range': '4.0-5.6',
                'min_value': 3,
                'max_value': 15,
                'icon': 'fas fa-chart-line',
                'color': '#4ecdc4'
            },
            {
                'metric_id': 'CHOL_TOTAL',
                'name': 'Total Cholesterol',
                'type': 'lab_result',
                'unit': 'mg/dL',
                'description': 'Total cholesterol level',
                'reference_range': '<200',
                'min_value': 50,
                'max_value': 500,
                'icon': 'fas fa-chart-bar',
                'color': '#45b7d1'
            },
            {
                'metric_id': 'CHOL_HDL',
                'name': 'HDL Cholesterol',
                'type': 'lab_result',
                'unit': 'mg/dL',
                'description': 'High-density lipoprotein cholesterol',
                'reference_range': '>40',
                'min_value': 10,
                'max_value': 200,
                'icon': 'fas fa-arrow-up',
                'color': '#96ceb4'
            },
            {
                'metric_id': 'CHOL_LDL',
                'name': 'LDL Cholesterol',
                'type': 'lab_result',
                'unit': 'mg/dL',
                'description': 'Low-density lipoprotein cholesterol',
                'reference_range': '<100',
                'min_value': 20,
                'max_value': 300,
                'icon': 'fas fa-arrow-down',
                'color': '#ffeaa7'
            },
            {
                'metric_id': 'TRIGLYCERIDES',
                'name': 'Triglycerides',
                'type': 'lab_result',
                'unit': 'mg/dL',
                'description': 'Triglyceride level',
                'reference_range': '<150',
                'min_value': 20,
                'max_value': 1000,
                'icon': 'fas fa-chart-pie',
                'color': '#dda0dd'
            },
            {
                'metric_id': 'VIT_D',
                'name': 'Vitamin D',
                'type': 'lab_result',
                'unit': 'ng/mL',
                'description': 'Vitamin D (25-OH) level',
                'reference_range': '30-100',
                'min_value': 5,
                'max_value': 200,
                'icon': 'fas fa-sun',
                'color': '#ffd93d'
            },
            {
                'metric_id': 'TESTOSTERONE',
                'name': 'Testosterone',
                'type': 'lab_result',
                'unit': 'ng/dL',
                'description': 'Total testosterone level',
                'reference_range': '300-1000',
                'min_value': 50,
                'max_value': 2000,
                'icon': 'fas fa-mars',
                'color': '#ff6b6b'
            },
            {
                'metric_id': 'CORTISOL',
                'name': 'Cortisol',
                'type': 'lab_result',
                'unit': 'μg/dL',
                'description': 'Cortisol level',
                'reference_range': '6.2-19.4',
                'min_value': 1,
                'max_value': 50,
                'icon': 'fas fa-brain',
                'color': '#a8edea'
            },
            {
                'metric_id': 'TSH',
                'name': 'TSH',
                'type': 'lab_result',
                'unit': 'μIU/mL',
                'description': 'Thyroid stimulating hormone',
                'reference_range': '0.4-4.0',
                'min_value': 0.01,
                'max_value': 100,
                'icon': 'fas fa-butterfly',
                'color': '#667eea'
            },
        ]

        # Vital signs
        vital_metrics = [
            {
                'metric_id': 'BP_SYS',
                'name': 'Blood Pressure Systolic',
                'type': 'vital_sign',
                'unit': 'mmHg',
                'description': 'Systolic blood pressure',
                'reference_range': '<120',
                'min_value': 60,
                'max_value': 250,
                'icon': 'fas fa-heartbeat',
                'color': '#ff6b6b'
            },
            {
                'metric_id': 'BP_DIA',
                'name': 'Blood Pressure Diastolic',
                'type': 'vital_sign',
                'unit': 'mmHg',
                'description': 'Diastolic blood pressure',
                'reference_range': '<80',
                'min_value': 40,
                'max_value': 150,
                'icon': 'fas fa-heartbeat',
                'color': '#4ecdc4'
            },
            {
                'metric_id': 'HR',
                'name': 'Heart Rate',
                'type': 'vital_sign',
                'unit': 'bpm',
                'description': 'Resting heart rate',
                'reference_range': '60-100',
                'min_value': 30,
                'max_value': 200,
                'icon': 'fas fa-heart',
                'color': '#ff6b6b'
            },
            {
                'metric_id': 'TEMP',
                'name': 'Body Temperature',
                'type': 'vital_sign',
                'unit': '°C',
                'description': 'Body temperature',
                'reference_range': '36.1-37.2',
                'min_value': 30,
                'max_value': 45,
                'icon': 'fas fa-thermometer-half',
                'color': '#ffa726'
            },
            {
                'metric_id': 'RESP_RATE',
                'name': 'Respiratory Rate',
                'type': 'vital_sign',
                'unit': 'breaths/min',
                'description': 'Respiratory rate',
                'reference_range': '12-20',
                'min_value': 5,
                'max_value': 50,
                'icon': 'fas fa-lungs',
                'color': '#81c784'
            },
        ]

        # Fitness metrics
        fitness_metrics = [
            {
                'metric_id': 'VO2_MAX',
                'name': 'VO2 Max',
                'type': 'fitness',
                'unit': 'mL/kg/min',
                'description': 'Maximum oxygen consumption',
                'min_value': 20,
                'max_value': 80,
                'icon': 'fas fa-running',
                'color': '#4facfe'
            },
            {
                'metric_id': 'HR_REST',
                'name': 'Resting Heart Rate',
                'type': 'fitness',
                'unit': 'bpm',
                'description': 'Resting heart rate',
                'reference_range': '60-100',
                'min_value': 30,
                'max_value': 200,
                'icon': 'fas fa-heart',
                'color': '#ff6b6b'
            },
            {
                'metric_id': 'HR_MAX',
                'name': 'Max Heart Rate',
                'type': 'fitness',
                'unit': 'bpm',
                'description': 'Maximum heart rate',
                'min_value': 100,
                'max_value': 220,
                'icon': 'fas fa-heart',
                'color': '#ff6b6b'
            },
        ]

        # Nutrition metrics
        nutrition_metrics = [
            {
                'metric_id': 'CALORIES_DAILY',
                'name': 'Daily Calories',
                'type': 'nutrition',
                'unit': 'kcal',
                'description': 'Daily caloric intake',
                'min_value': 500,
                'max_value': 5000,
                'icon': 'fas fa-fire',
                'color': '#ffa726'
            },
            {
                'metric_id': 'PROTEIN',
                'name': 'Protein Intake',
                'type': 'nutrition',
                'unit': 'g',
                'description': 'Daily protein intake',
                'min_value': 0,
                'max_value': 500,
                'icon': 'fas fa-drumstick-bite',
                'color': '#8d6e63'
            },
            {
                'metric_id': 'CARBS',
                'name': 'Carbohydrate Intake',
                'type': 'nutrition',
                'unit': 'g',
                'description': 'Daily carbohydrate intake',
                'min_value': 0,
                'max_value': 1000,
                'icon': 'fas fa-bread-slice',
                'color': '#ffd54f'
            },
            {
                'metric_id': 'FAT',
                'name': 'Fat Intake',
                'type': 'nutrition',
                'unit': 'g',
                'description': 'Daily fat intake',
                'min_value': 0,
                'max_value': 200,
                'icon': 'fas fa-oil-can',
                'color': '#ffb74d'
            },
        ]

        all_metrics = body_metrics + calculated_metrics + lab_metrics + vital_metrics + fitness_metrics + nutrition_metrics
        
        created_count = 0
        updated_count = 0
        for metric_data in all_metrics:
            metric, created = Metric.objects.get_or_create(
                name=metric_data['name'],
                defaults=metric_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created metric: {metric.name}")
            else:
                # Update existing metric with new data
                for key, value in metric_data.items():
                    setattr(metric, key, value)
                metric.save()
                updated_count += 1
                self.stdout.write(f"Updated metric: {metric.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} metrics and updated {updated_count} metrics!')
        )
