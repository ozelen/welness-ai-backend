from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from activities.models import Exercise


class Command(BaseCommand):
    help = 'Populate default exercises'

    def handle(self, *args, **options):
        # Default exercises
        default_exercises = [
            # Cardio exercises
            {
                'name': 'Running',
                'description': 'Outdoor or treadmill running at moderate pace',
                'category': 'Cardio',
                'muscle_groups': 'Legs, Cardiovascular',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Running shoes, treadmill (optional)',
                'calories_per_hour_per_kg': 11.5,
            },
            {
                'name': 'Cycling',
                'description': 'Indoor or outdoor cycling',
                'category': 'Cardio',
                'muscle_groups': 'Legs, Cardiovascular',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Bicycle, helmet',
                'calories_per_hour_per_kg': 8.0,
            },
            {
                'name': 'Swimming',
                'description': 'Freestyle swimming in pool',
                'category': 'Cardio',
                'muscle_groups': 'Full body, Cardiovascular',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Swimsuit, goggles',
                'calories_per_hour_per_kg': 9.0,
            },
            {
                'name': 'Jump Rope',
                'description': 'Skipping rope for cardio workout',
                'category': 'Cardio',
                'muscle_groups': 'Legs, Shoulders, Cardiovascular',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Jump rope',
                'calories_per_hour_per_kg': 12.0,
            },
            
            # Strength exercises
            {
                'name': 'Push-ups',
                'description': 'Bodyweight chest and triceps exercise',
                'category': 'Strength',
                'muscle_groups': 'Chest, Triceps, Shoulders',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'None',
                'calories_per_hour_per_kg': 4.0,
            },
            {
                'name': 'Squats',
                'description': 'Bodyweight leg exercise',
                'category': 'Strength',
                'muscle_groups': 'Quadriceps, Glutes, Hamstrings',
                'difficulty_level': 'beginner',
                'equipment_needed': 'None',
                'calories_per_hour_per_kg': 5.0,
            },
            {
                'name': 'Pull-ups',
                'description': 'Upper body pulling exercise',
                'category': 'Strength',
                'muscle_groups': 'Back, Biceps, Shoulders',
                'difficulty_level': 'advanced',
                'equipment_needed': 'Pull-up bar',
                'calories_per_hour_per_kg': 6.0,
            },
            {
                'name': 'Plank',
                'description': 'Core stability exercise',
                'category': 'Strength',
                'muscle_groups': 'Core, Shoulders',
                'difficulty_level': 'beginner',
                'equipment_needed': 'None',
                'calories_per_hour_per_kg': 3.0,
            },
            {
                'name': 'Deadlift',
                'description': 'Compound lower body exercise with weights',
                'category': 'Strength',
                'muscle_groups': 'Back, Glutes, Hamstrings, Core',
                'difficulty_level': 'advanced',
                'equipment_needed': 'Barbell, weights',
                'calories_per_hour_per_kg': 7.0,
            },
            {
                'name': 'Bench Press',
                'description': 'Compound chest exercise with weights',
                'category': 'Strength',
                'muscle_groups': 'Chest, Triceps, Shoulders',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Barbell, bench, weights',
                'calories_per_hour_per_kg': 6.0,
            },
            
            # Flexibility exercises
            {
                'name': 'Stretching',
                'description': 'General flexibility and mobility work',
                'category': 'Flexibility',
                'muscle_groups': 'Full body',
                'difficulty_level': 'beginner',
                'equipment_needed': 'None',
                'calories_per_hour_per_kg': 2.0,
            },
            {
                'name': 'Yoga',
                'description': 'Mind-body practice combining physical postures and breathing',
                'category': 'Flexibility',
                'muscle_groups': 'Full body',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Yoga mat',
                'calories_per_hour_per_kg': 3.5,
            },
            {
                'name': 'Pilates',
                'description': 'Core-focused exercise system',
                'category': 'Flexibility',
                'muscle_groups': 'Core, Full body',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Mat (optional equipment)',
                'calories_per_hour_per_kg': 3.0,
            },
            
            # Sports
            {
                'name': 'Basketball',
                'description': 'Team sport with running, jumping, and coordination',
                'category': 'Sports',
                'muscle_groups': 'Full body, Cardiovascular',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Basketball, court',
                'calories_per_hour_per_kg': 8.5,
            },
            {
                'name': 'Tennis',
                'description': 'Racket sport requiring agility and coordination',
                'category': 'Sports',
                'muscle_groups': 'Arms, Legs, Core',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Tennis racket, balls, court',
                'calories_per_hour_per_kg': 7.0,
            },
            {
                'name': 'Soccer',
                'description': 'Team sport with running and ball control',
                'category': 'Sports',
                'muscle_groups': 'Legs, Cardiovascular',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Soccer ball, field',
                'calories_per_hour_per_kg': 8.0,
            },
            
            # Work activities
            {
                'name': 'Walking',
                'description': 'Casual walking for transportation or leisure',
                'category': 'Work',
                'muscle_groups': 'Legs',
                'difficulty_level': 'beginner',
                'equipment_needed': 'Comfortable shoes',
                'calories_per_hour_per_kg': 3.5,
            },
            {
                'name': 'Standing',
                'description': 'Standing work or activities',
                'category': 'Work',
                'muscle_groups': 'Legs, Core',
                'difficulty_level': 'beginner',
                'equipment_needed': 'None',
                'calories_per_hour_per_kg': 1.5,
            },
            {
                'name': 'Manual Labor',
                'description': 'Physical work requiring lifting and movement',
                'category': 'Work',
                'muscle_groups': 'Full body',
                'difficulty_level': 'intermediate',
                'equipment_needed': 'Work tools',
                'calories_per_hour_per_kg': 6.0,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for exercise_data in default_exercises:
            exercise, created = Exercise.objects.get_or_create(
                name=exercise_data['name'],
                defaults={
                    'description': exercise_data['description'],
                    'category': exercise_data['category'],
                    'muscle_groups': exercise_data['muscle_groups'],
                    'difficulty_level': exercise_data['difficulty_level'],
                    'equipment_needed': exercise_data['equipment_needed'],
                    'calories_per_hour_per_kg': exercise_data['calories_per_hour_per_kg'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {exercise.name}')
                )
            else:
                # Update existing record
                exercise.description = exercise_data['description']
                exercise.category = exercise_data['category']
                exercise.muscle_groups = exercise_data['muscle_groups']
                exercise.difficulty_level = exercise_data['difficulty_level']
                exercise.equipment_needed = exercise_data['equipment_needed']
                exercise.calories_per_hour_per_kg = exercise_data['calories_per_hour_per_kg']
                exercise.is_active = True
                exercise.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {exercise.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(default_exercises)} exercises. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
