from django.core.management.base import BaseCommand
from agents.models import Tool


class Command(BaseCommand):
    help = 'Populate the database with available tools for agents'

    def handle(self, *args, **options):
        self.stdout.write('Creating tools...')
        
        tools_data = [
            {
                'name': 'get_user_goals',
                'display_name': 'Get User Goals',
                'description': 'Get all active goals for a specific user',
                'function_name': 'get_user_goals',
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'The ID of the user'
                        }
                    },
                    'required': ['user_id']
                }
            },
            {
                'name': 'get_user_body_measurements',
                'display_name': 'Get User Body Measurements',
                'description': 'Get body measurements for a specific user, optionally filtered by goal',
                'function_name': 'get_user_body_measurements',
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'The ID of the user'
                        },
                        'goal_id': {
                            'type': 'string',
                            'description': 'Optional goal ID to filter measurements'
                        }
                    },
                    'required': ['user_id']
                }
            },
            {
                'name': 'get_user_progress_summary',
                'display_name': 'Get User Progress Summary',
                'description': 'Get a comprehensive summary of user\'s goals and progress',
                'function_name': 'get_user_progress_summary',
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'The ID of the user'
                        }
                    },
                    'required': ['user_id']
                }
            },
            {
                'name': 'search_goals_by_type',
                'display_name': 'Search Goals by Type',
                'description': 'Search for goals by type for a specific user',
                'function_name': 'search_goals_by_type',
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'The ID of the user'
                        },
                        'goal_type': {
                            'type': 'string',
                            'description': 'The type of goal to search for (e.g., \'weight_loss\', \'muscle_gain\')'
                        }
                    },
                    'required': ['user_id', 'goal_type']
                }
            },
            {
                'name': 'get_latest_measurements',
                'display_name': 'Get Latest Measurements',
                'description': 'Get the latest measurements for a user, optionally filtered by metric',
                'function_name': 'get_latest_measurements',
                'parameters_schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'The ID of the user'
                        },
                        'metric': {
                            'type': 'string',
                            'description': 'Optional metric to filter by (e.g., \'weight_kg\', \'body_fat_percentage\')'
                        }
                    },
                    'required': ['user_id']
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for tool_data in tools_data:
            tool, created = Tool.objects.update_or_create(
                name=tool_data['name'],
                defaults={
                    'display_name': tool_data['display_name'],
                    'description': tool_data['description'],
                    'function_name': tool_data['function_name'],
                    'parameters_schema': tool_data['parameters_schema'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created tool: {tool.display_name}')
            else:
                updated_count += 1
                self.stdout.write(f'Updated tool: {tool.display_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(tools_data)} tools. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        ) 