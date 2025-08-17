from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from metrics.models import Metric

class Command(BaseCommand):
    help = 'Update existing metrics with metric IDs'

    def handle(self, *args, **options):
        self.stdout.write('Updating metrics with metric IDs...')
        
        # Define metric ID mappings
        metric_id_mappings = {
            'Weight': 'WEIGHT',
            'Height': 'HEIGHT',
            'Body Fat Percentage': 'BF_PCT',
            'BMI': 'BMI',
            'Lean Body Mass': 'LBM',
            'Body Fat Mass': 'BF_MASS',
            'Basal Metabolic Rate': 'BMR',
            'Total Daily Energy Expenditure': 'TDEE',
            'Waist Circumference': 'WAIST_CIRC',
            'Hip Circumference': 'HIP_CIRC',
            'Chest Circumference': 'CHEST_CIRC',
            'Neck Circumference': 'NECK_CIRC',
            'Arm Circumference': 'ARM_CIRC',
            'Thigh Circumference': 'THIGH_CIRC',
            'Calf Circumference': 'CALF_CIRC',
            'Muscle Mass Percentage': 'MUSCLE_PCT',
            'Body Water Percentage': 'BW_PCT',
            'Bone Mass': 'BONE_MASS',
            'Visceral Fat': 'VISCERAL_FAT',
            'Blood Glucose': 'GLUCOSE',
            'Hemoglobin A1c': 'HBA1C',
            'Total Cholesterol': 'CHOL_TOTAL',
            'HDL Cholesterol': 'CHOL_HDL',
            'LDL Cholesterol': 'CHOL_LDL',
            'Triglycerides': 'TRIGLYCERIDES',
            'Vitamin D': 'VIT_D',
            'Testosterone': 'TESTOSTERONE',
            'Blood Pressure Systolic': 'BP_SYS',
            'Blood Pressure Diastolic': 'BP_DIA',
            'Heart Rate': 'HR',
            'Body Temperature': 'TEMP',
            'VO2 Max': 'VO2_MAX',
            'Resting Heart Rate': 'HR_REST',
            'Daily Calories': 'CALORIES_DAILY',
            'Protein Intake': 'PROTEIN',
            'Carbohydrate Intake': 'CARBS',
            'Fat Intake': 'FAT',
        }
        
        updated_count = 0
        for metric_name, metric_id in metric_id_mappings.items():
            try:
                metric = Metric.objects.get(name=metric_name)
                if not metric.metric_id:
                    metric.metric_id = metric_id
                    metric.save()
                    updated_count += 1
                    self.stdout.write(f"Updated {metric_name} with ID: {metric_id}")
            except Metric.DoesNotExist:
                self.stdout.write(f"Metric not found: {metric_name}")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} metrics with IDs!'))
