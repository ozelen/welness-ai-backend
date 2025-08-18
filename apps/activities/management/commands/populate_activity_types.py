from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from activities.models import ActivityType


class Command(BaseCommand):
    help = 'Populate default activity types from deficits.csv data'

    def handle(self, *args, **options):
        # Default activity types with calories per hour per kg
        default_activities = [
            # Work activities
            {
                'name': 'sedentary_work',
                'display_name': 'Sedentary work (office)',
                'calories_per_hour_per_kg': 1.2,
                'category': 'Work'
            },
            {
                'name': 'standing_work',
                'display_name': 'Standing work',
                'calories_per_hour_per_kg': 2.0,
                'category': 'Work'
            },
            {
                'name': 'physical_labor',
                'display_name': 'Physical labor (Gardening, Manual construction work, etc.)',
                'calories_per_hour_per_kg': 5.0,
                'category': 'Work'
            },
            {
                'name': 'physical_work',
                'display_name': 'Physical work (work of a loader, with weight transfer)',
                'calories_per_hour_per_kg': 7.0,
                'category': 'Work'
            },
            
            # Strength training
            {
                'name': 'strength_training_no_failure',
                'display_name': 'Strength training (without failure approaches)',
                'calories_per_hour_per_kg': 3.0,
                'category': 'Strength'
            },
            {
                'name': 'strength_training_with_failure',
                'display_name': 'Strength Training (with failure approaches)',
                'calories_per_hour_per_kg': 6.0,
                'category': 'Strength'
            },
            
            # Running
            {
                'name': 'running_slow',
                'display_name': 'Running slowly (~8 km/h)',
                'calories_per_hour_per_kg': 8.2,
                'category': 'Cardio'
            },
            {
                'name': 'running_moderate',
                'display_name': 'Moderate running (~10 km/h)',
                'calories_per_hour_per_kg': 10.3,
                'category': 'Cardio'
            },
            {
                'name': 'running_fast',
                'display_name': 'Running fast (~12 km/h)',
                'calories_per_hour_per_kg': 12.9,
                'category': 'Cardio'
            },
            {
                'name': 'interval_running',
                'display_name': 'Interval running (sprints/running)',
                'calories_per_hour_per_kg': 12.0,
                'category': 'Cardio'
            },
            
            # Cardio equipment
            {
                'name': 'orbitrek_medium',
                'display_name': 'Orbitrek medium intense.',
                'calories_per_hour_per_kg': 9.3,
                'category': 'Cardio'
            },
            {
                'name': 'exercise_bike_moderate',
                'display_name': 'Moderate speed exercise bike.',
                'calories_per_hour_per_kg': 7.4,
                'category': 'Cardio'
            },
            {
                'name': 'exercise_bike_high',
                'display_name': 'High intensity exercise bike.',
                'calories_per_hour_per_kg': 11.2,
                'category': 'Cardio'
            },
            {
                'name': 'stepper_medium',
                'display_name': 'Stepper medium intensity.',
                'calories_per_hour_per_kg': 6.2,
                'category': 'Cardio'
            },
            
            # Walking
            {
                'name': 'walking_moderate',
                'display_name': 'Walking moderately fast. (~5–6 km/h)',
                'calories_per_hour_per_kg': 3.8,
                'category': 'Cardio'
            },
            
            # High intensity
            {
                'name': 'hiit',
                'display_name': 'HIIT (intervals)',
                'calories_per_hour_per_kg': 12.0,
                'category': 'High Intensity'
            },
            {
                'name': 'crossfit',
                'display_name': 'Crossfit',
                'calories_per_hour_per_kg': 13.7,
                'category': 'High Intensity'
            },
            
            # Flexibility/Mind-body
            {
                'name': 'yoga_hatha',
                'display_name': 'Yoga (hatha)',
                'calories_per_hour_per_kg': 4.1,
                'category': 'Flexibility'
            },
            {
                'name': 'pilates_basic',
                'display_name': 'Pilates (mat, basic)',
                'calories_per_hour_per_kg': 3.3,
                'category': 'Flexibility'
            },
            
            # Dancing
            {
                'name': 'dancing_slow',
                'display_name': 'Dancing (slow)',
                'calories_per_hour_per_kg': 3.1,
                'category': 'Dance'
            },
            {
                'name': 'dancing_energetic',
                'display_name': 'Dancing (energetic)',
                'calories_per_hour_per_kg': 6.2,
                'category': 'Dance'
            },
            
            # Combat sports
            {
                'name': 'boxing',
                'display_name': 'Boxing / kickboxing',
                'calories_per_hour_per_kg': 9.6,
                'category': 'Combat'
            },
            
            # Swimming
            {
                'name': 'swimming_calm',
                'display_name': 'Swimming (calm)',
                'calories_per_hour_per_kg': 6.2,
                'category': 'Swimming'
            },
            {
                'name': 'swimming_intense',
                'display_name': 'Swimming (intense)',
                'calories_per_hour_per_kg': 10.3,
                'category': 'Swimming'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for activity_data in default_activities:
            activity_type, created = ActivityType.objects.get_or_create(
                name=activity_data['name'],
                defaults={
                    'display_name': activity_data['display_name'],
                    'calories_per_hour_per_kg': activity_data['calories_per_hour_per_kg'],
                    'category': activity_data['category'],
                    'is_default': True,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {activity_type.display_name}')
                )
            else:
                # Update existing record
                activity_type.display_name = activity_data['display_name']
                activity_type.calories_per_hour_per_kg = activity_data['calories_per_hour_per_kg']
                activity_type.category = activity_data['category']
                activity_type.is_default = True
                activity_type.is_active = True
                activity_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {activity_type.display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(default_activities)} activity types. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
