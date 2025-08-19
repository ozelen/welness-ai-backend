from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from activities.models import ActivityType

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate default activity types with exercise schemas'

    def handle(self, *args, **options):
        # Get or create a system user for default activities
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'is_active': False
            }
        )

        # Define activity types with their exercise schemas
        activity_types_data = [
            {
                'name': 'running',
                'display_name': 'Running',
                'calories_per_hour_per_kg': 8.0,
                'category': 'cardio',
                'is_default': True,
                'exercise_schema': {
                    'type': 'object',
                    'properties': {
                        'duration_minutes': {
                            'type': 'integer',
                            'description': 'Duration in minutes',
                            'default': 30,
                            'minimum': 1
                        },
                        'distance_km': {
                            'type': 'number',
                            'description': 'Distance in kilometers',
                            'minimum': 0
                        },
                        'pace_min_per_km': {
                            'type': 'number',
                            'description': 'Pace in minutes per kilometer'
                        }
                    },
                    'required': ['duration_minutes']
                }
            },
            {
                'name': 'strength_training',
                'display_name': 'Strength Training',
                'calories_per_hour_per_kg': 4.0,
                'category': 'strength',
                'is_default': True,
                'exercise_schema': {
                    'type': 'object',
                    'properties': {
                        'duration_minutes': {
                            'type': 'integer',
                            'description': 'Duration in minutes',
                            'default': 45,
                            'minimum': 1
                        },
                        'sets': {
                            'type': 'integer',
                            'description': 'Number of sets',
                            'default': 3,
                            'minimum': 1
                        },
                        'reps': {
                            'type': 'integer',
                            'description': 'Number of repetitions per set',
                            'minimum': 1
                        },
                        'weight_kg': {
                            'type': 'number',
                            'description': 'Weight in kilograms',
                            'minimum': 0
                        },
                        'rest_minutes': {
                            'type': 'integer',
                            'description': 'Rest time between sets in minutes',
                            'default': 2
                        }
                    },
                    'required': ['duration_minutes', 'sets']
                }
            },
            {
                'name': 'cycling',
                'display_name': 'Cycling',
                'calories_per_hour_per_kg': 6.0,
                'category': 'cardio',
                'is_default': True,
                'exercise_schema': {
                    'type': 'object',
                    'properties': {
                        'duration_minutes': {
                            'type': 'integer',
                            'description': 'Duration in minutes',
                            'default': 30,
                            'minimum': 1
                        },
                        'distance_km': {
                            'type': 'number',
                            'description': 'Distance in kilometers',
                            'minimum': 0
                        },
                        'speed_kmh': {
                            'type': 'number',
                            'description': 'Average speed in km/h'
                        }
                    },
                    'required': ['duration_minutes']
                }
            },
            {
                'name': 'yoga',
                'display_name': 'Yoga',
                'calories_per_hour_per_kg': 2.5,
                'category': 'flexibility',
                'is_default': True,
                'exercise_schema': {
                    'type': 'object',
                    'properties': {
                        'duration_minutes': {
                            'type': 'integer',
                            'description': 'Duration in minutes',
                            'default': 60,
                            'minimum': 1
                        },
                        'style': {
                            'type': 'string',
                            'description': 'Yoga style (e.g., Hatha, Vinyasa, Ashtanga)',
                            'enum': ['Hatha', 'Vinyasa', 'Ashtanga', 'Bikram', 'Restorative', 'Other']
                        }
                    },
                    'required': ['duration_minutes']
                }
            },
            {
                'name': 'swimming',
                'display_name': 'Swimming',
                'calories_per_hour_per_kg': 7.0,
                'category': 'cardio',
                'is_default': True,
                'exercise_schema': {
                    'type': 'object',
                    'properties': {
                        'duration_minutes': {
                            'type': 'integer',
                            'description': 'Duration in minutes',
                            'default': 30,
                            'minimum': 1
                        },
                        'distance_m': {
                            'type': 'number',
                            'description': 'Distance in meters',
                            'minimum': 0
                        },
                        'stroke': {
                            'type': 'string',
                            'description': 'Swimming stroke',
                            'enum': ['Freestyle', 'Breaststroke', 'Backstroke', 'Butterfly', 'Mixed']
                        }
                    },
                    'required': ['duration_minutes']
                }
            }
        ]

        created_count = 0
        updated_count = 0

        for data in activity_types_data:
            activity_type, created = ActivityType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'display_name': data['display_name'],
                    'calories_per_hour_per_kg': data['calories_per_hour_per_kg'],
                    'category': data['category'],
                    'is_default': data['is_default'],
                    'exercise_schema': data['exercise_schema'],
                    'created_by': system_user
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created activity type: {activity_type.display_name}')
                )
            else:
                # Update existing activity type with new schema
                activity_type.exercise_schema = data['exercise_schema']
                activity_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated activity type: {activity_type.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(activity_types_data)} activity types. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
