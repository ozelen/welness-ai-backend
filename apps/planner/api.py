from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from meals.models import Meal, MealRecord
from activities.models import Activity, ActivityRecord
import json

@api_view(['GET'])
@permission_classes([AllowAny])  # Temporarily disabled for testing
def get_scheduler_events(request):
    """Get all events for the scheduler"""
    start_date = request.GET.get('start', timezone.now().date().isoformat())
    end_date = request.GET.get('end', (timezone.now().date() + timedelta(days=7)).isoformat())
    
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
    except ValueError:
        return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
    
    events = []
    
    # For testing, use a default user if not authenticated
    user = request.user if request.user.is_authenticated else None
    if not user:
        # Try to get user with ID 1 for testing
        from django.contrib.auth.models import User
        user = User.objects.filter(id=1).first()
        if not user:
            return Response({'error': 'User with ID 1 not found for testing'}, status=status.HTTP_400_BAD_REQUEST)
    
    print(f"DEBUG: Using user: {user.username if user else 'None'} (ID: {user.id if user else 'None'})")
    print(f"DEBUG: Date range: {start} to {end}")
    
    # Get planned meals
    planned_meals = Meal.objects.filter(
        diet__user=user,
        start_date__gte=start,
        start_date__lte=end
    )
    print(f"DEBUG: Found {planned_meals.count()} planned meals")
    
    # Debug: Check all meals for this user
    all_meals = Meal.objects.filter(diet__user=user)
    print(f"DEBUG: Total meals for user: {all_meals.count()}")
    if all_meals.exists():
        print(f"DEBUG: First meal dates: {[m.start_date for m in all_meals[:5]]}")
    
    for meal in planned_meals:
        # Generate events based on recurrence
        if meal.recurrence_type == 'none':
            if start <= meal.start_date <= end:
                events.append({
                    'Id': f'meal_{meal.id}',
                    'Subject': meal.name,
                    'StartTime': datetime.combine(meal.start_date, meal.start_time or datetime.min.time()),
                    'EndTime': datetime.combine(meal.start_date, meal.start_time or datetime.min.time()) + timedelta(minutes=meal.duration_minutes or 30),
                    'EventType': 'meal',
                    'CategoryColor': '#4CAF50',
                    'Calories': meal.get_total_calories(),
                    'Proteins': 0,  # TODO: Add these methods to Meal model
                    'Carbs': 0,
                    'Fats': 0,
                    'IsCompleted': False,  # TODO: Check if completed
                    'RecurrenceType': meal.recurrence_type,
                    'Notes': meal.description
                })
        elif meal.recurrence_type == 'daily':
            current_date = start
            while current_date <= end:
                if meal.start_date <= current_date <= (meal.end_date or end):
                    events.append({
                        'Id': f'meal_{meal.id}_{current_date}',
                        'Subject': meal.name,
                        'StartTime': datetime.combine(current_date, meal.start_time or datetime.min.time()),
                        'EndTime': datetime.combine(current_date, meal.start_time or datetime.min.time()) + timedelta(minutes=meal.duration_minutes or 30),
                        'EventType': 'meal',
                        'CategoryColor': '#4CAF50',
                        'Calories': meal.get_total_calories(),
                        'Proteins': 0,
                        'Carbs': 0,
                        'Fats': 0,
                        'IsCompleted': False,
                        'RecurrenceType': meal.recurrence_type,
                        'Notes': meal.description
                    })
                current_date += timedelta(days=1)
        # Add other recurrence types as needed
    
    # Get planned activities
    planned_activities = Activity.objects.filter(
        user=user,
        start_date__gte=start,
        start_date__lte=end
    )
    print(f"DEBUG: Found {planned_activities.count()} planned activities")
    
    # Debug: Check all activities for this user
    all_activities = Activity.objects.filter(user=user)
    print(f"DEBUG: Total activities for user: {all_activities.count()}")
    if all_activities.exists():
        print(f"DEBUG: First activity dates: {[a.start_date for a in all_activities[:5]]}")
    
    for activity in planned_activities:
        if activity.recurrence_type == 'none':
            if start <= activity.start_date <= end:
                events.append({
                    'Id': f'activity_{activity.id}',
                    'Subject': activity.name or activity.activity_type.display_name,
                    'StartTime': datetime.combine(activity.start_date, activity.start_time or datetime.min.time()),
                    'EndTime': datetime.combine(activity.start_date, activity.start_time or datetime.min.time()) + timedelta(hours=activity.duration_hours or 1),
                    'EventType': 'activity',
                    'CategoryColor': '#FF9800',
                    'CaloriesBurned': activity.calories_burned,
                    'Duration': int((activity.duration_hours or 1) * 60),
                    'IsCompleted': False,
                    'RecurrenceType': activity.recurrence_type,
                    'Notes': activity.notes
                })
        elif activity.recurrence_type == 'daily':
            current_date = start
            while current_date <= end:
                if activity.start_date <= current_date <= (activity.recurrence_until or end):
                    events.append({
                        'Id': f'activity_{activity.id}_{current_date}',
                        'Subject': activity.name or activity.activity_type.display_name,
                        'StartTime': datetime.combine(current_date, activity.start_time or datetime.min.time()),
                        'EndTime': datetime.combine(current_date, activity.start_time or datetime.min.time()) + timedelta(hours=activity.duration_hours or 1),
                        'EventType': 'activity',
                        'CategoryColor': '#FF9800',
                        'CaloriesBurned': activity.calories_burned,
                        'Duration': int((activity.duration_hours or 1) * 60),
                        'IsCompleted': False,
                        'RecurrenceType': activity.recurrence_type,
                        'Notes': activity.notes
                    })
                current_date += timedelta(days=1)
    
    # Get logged meal records
    meal_records = MealRecord.objects.filter(
        user=user,
        timestamp__date__gte=start,
        timestamp__date__lte=end
    )
    
    for record in meal_records:
        events.append({
            'Id': f'meal_record_{record.id}',
            'Subject': record.meal.name if record.meal else record.meal_name,
            'StartTime': record.timestamp,
            'EndTime': record.timestamp + timedelta(minutes=30),
            'EventType': 'meal_record',
            'CategoryColor': '#2196F3',
            'Calories': record.calories,
            'Proteins': record.proteins,
            'Carbs': record.carbs,
            'Fats': record.fats,
            'IsCompleted': True,
            'Notes': record.feedback
        })
    
    # Get logged activity records
    activity_records = ActivityRecord.objects.filter(
        user=user,
        date__gte=start,
        date__lte=end
    )
    
    for record in activity_records:
        events.append({
            'Id': f'activity_record_{record.id}',
            'Subject': record.activity.name if record.activity else record.activity_name,
            'StartTime': datetime.combine(record.date, record.start_time or datetime.min.time()),
            'EndTime': datetime.combine(record.date, record.start_time or datetime.min.time()) + timedelta(hours=record.duration_hours or 1),
            'EventType': 'activity_record',
            'CategoryColor': '#9C27B0',
            'CaloriesBurned': record.get_calories_burned(),
            'Duration': int((record.duration_hours or 1) * 60),
            'IsCompleted': True,
            'Notes': record.notes
        })
    
    return Response(events)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_scheduler_event(request):
    """Create a new event from the scheduler"""
    try:
        data = request.data
        event_type = data.get('EventType')
        
        if event_type == 'meal':
            # Create a new meal
            meal = Meal.objects.create(
                diet=request.user.diet_set.filter(is_active=True).first(),
                name=data.get('Subject'),
                start_date=data.get('StartTime').split('T')[0],
                start_time=data.get('StartTime').split('T')[1][:5],
                duration_minutes=30,  # Default
                description=data.get('Notes', '')
            )
            return Response({
                'success': True,
                'event': {
                    'Id': f'meal_{meal.id}',
                    'Subject': meal.name,
                    'StartTime': meal.start_time,
                    'EndTime': meal.start_time,
                    'EventType': 'meal',
                    'CategoryColor': '#4CAF50'
                }
            })
        
        elif event_type == 'activity':
            # Create a new activity
            activity = Activity.objects.create(
                user=request.user,
                name=data.get('Subject'),
                start_date=data.get('StartTime').split('T')[0],
                start_time=data.get('StartTime').split('T')[1][:5],
                duration_hours=1,  # Default
                notes=data.get('Notes', '')
            )
            return Response({
                'success': True,
                'event': {
                    'Id': f'activity_{activity.id}',
                    'Subject': activity.name,
                    'StartTime': activity.start_time,
                    'EndTime': activity.start_time,
                    'EventType': 'activity',
                    'CategoryColor': '#FF9800'
                }
            })
        
        else:
            return Response({'error': 'Invalid event type'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_scheduler_event(request, event_id):
    """Update an existing event"""
    try:
        data = request.data
        event_parts = event_id.split('_')
        
        if event_parts[0] == 'meal' and len(event_parts) >= 2:
            meal_id = event_parts[1]
            meal = Meal.objects.get(id=meal_id, diet__user=request.user)
            meal.name = data.get('Subject', meal.name)
            meal.start_date = data.get('StartTime').split('T')[0]
            meal.start_time = data.get('StartTime').split('T')[1][:5]
            meal.description = data.get('Notes', meal.description)
            meal.save()
            
        elif event_parts[0] == 'activity' and len(event_parts) >= 2:
            activity_id = event_parts[1]
            activity = Activity.objects.get(id=activity_id, user=request.user)
            activity.name = data.get('Subject', activity.name)
            activity.start_date = data.get('StartTime').split('T')[0]
            activity.start_time = data.get('StartTime').split('T')[1][:5]
            activity.notes = data.get('Notes', activity.notes)
            activity.save()
            
        return Response({'success': True})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_scheduler_event(request, event_id):
    """Delete an event"""
    try:
        event_parts = event_id.split('_')
        
        if event_parts[0] == 'meal' and len(event_parts) >= 2:
            meal_id = event_parts[1]
            meal = Meal.objects.get(id=meal_id, diet__user=request.user)
            meal.delete()
            
        elif event_parts[0] == 'activity' and len(event_parts) >= 2:
            activity_id = event_parts[1]
            activity = Activity.objects.get(id=activity_id, user=request.user)
            activity.delete()
            
        return Response({'success': True})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_simple(request):
    """Simple test endpoint with real data"""
    from datetime import datetime, timedelta
    from django.contrib.auth.models import User
    
    # Get user (for testing, use first user)
    user = User.objects.first()
    if not user:
        return Response({'error': 'No users found'}, status=400)
    
    # Get date range (current week)
    today = datetime.now().date()
    start_date = today - timedelta(days=7)
    end_date = today + timedelta(days=7)
    
    events = []
    
    # Get planned meals
    planned_meals = Meal.objects.filter(
        diet__user=user,
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    for meal in planned_meals:
        if meal.start_date and meal.start_time:
            start_time = datetime.combine(meal.start_date, meal.start_time)
            end_time = start_time + timedelta(minutes=meal.duration_minutes or 30)
            
            events.append({
                'Id': f'meal_{meal.id}',
                'Subject': meal.name,
                'StartTime': start_time.isoformat(),
                'EndTime': end_time.isoformat(),
                'EventType': 'meal',
                'CategoryColor': '#4CAF50',
                'Calories': meal.get_total_calories(),
                'Proteins': 0,  # TODO: Add these methods
                'Carbs': 0,
                'Fats': 0,
                'IsCompleted': False,
                'Notes': meal.description or ''
            })
    
    # Get planned activities
    planned_activities = Activity.objects.filter(
        user=user,
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    
    for activity in planned_activities:
        if activity.start_date and activity.start_time:
            start_time = datetime.combine(activity.start_date, activity.start_time)
            end_time = start_time + timedelta(hours=activity.duration_hours or 1)
            
            events.append({
                'Id': f'activity_{activity.id}',
                'Subject': activity.name or activity.activity_type.display_name,
                'StartTime': start_time.isoformat(),
                'EndTime': end_time.isoformat(),
                'EventType': 'activity',
                'CategoryColor': '#FF9800',
                'CaloriesBurned': activity.calories_burned,
                'Duration': int((activity.duration_hours or 1) * 60),
                'IsCompleted': False,
                'Notes': activity.notes or ''
            })
    
    # Get logged meal records
    meal_records = MealRecord.objects.filter(
        user=user,
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    )
    
    for record in meal_records:
        events.append({
            'Id': f'meal_record_{record.id}',
            'Subject': record.meal.name if record.meal else record.meal_name,
            'StartTime': record.timestamp.isoformat(),
            'EndTime': (record.timestamp + timedelta(minutes=30)).isoformat(),
            'EventType': 'meal_record',
            'CategoryColor': '#2196F3',
            'Calories': record.calories,
            'Proteins': record.proteins,
            'Carbs': record.carbs,
            'Fats': record.fats,
            'IsCompleted': True,
            'Notes': record.feedback or ''
        })
    
    # Get logged activity records
    activity_records = ActivityRecord.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    for record in activity_records:
        if record.start_time:
            start_time = datetime.combine(record.date, record.start_time)
            end_time = start_time + timedelta(hours=record.duration_hours or 1)
        else:
            start_time = datetime.combine(record.date, datetime.min.time())
            end_time = start_time + timedelta(hours=record.duration_hours or 1)
        
        events.append({
            'Id': f'activity_record_{record.id}',
            'Subject': record.activity.name if record.activity else record.activity_name,
            'StartTime': start_time.isoformat(),
            'EndTime': end_time.isoformat(),
            'EventType': 'activity_record',
            'CategoryColor': '#9C27B0',
            'CaloriesBurned': record.get_calories_burned(),
            'Duration': int((record.duration_hours or 1) * 60),
            'IsCompleted': True,
            'Notes': record.notes or ''
        })
    
    # If no real data, add some sample data for testing
    if not events:
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        events = [
            {
                'Id': 'sample_1',
                'Subject': 'Sample Breakfast',
                'StartTime': today.replace(hour=8, minute=0, second=0, microsecond=0).isoformat(),
                'EndTime': today.replace(hour=8, minute=30, second=0, microsecond=0).isoformat(),
                'EventType': 'meal',
                'CategoryColor': '#4CAF50',
                'Calories': 300,
                'Proteins': 20,
                'Carbs': 30,
                'Fats': 10,
                'IsCompleted': False,
                'Notes': 'Sample meal'
            },
            {
                'Id': 'sample_2',
                'Subject': 'Sample Workout',
                'StartTime': today.replace(hour=17, minute=0, second=0, microsecond=0).isoformat(),
                'EndTime': today.replace(hour=18, minute=0, second=0, microsecond=0).isoformat(),
                'EventType': 'activity',
                'CategoryColor': '#FF9800',
                'CaloriesBurned': 500,
                'Duration': 60,
                'IsCompleted': False,
                'Notes': 'Sample activity'
            }
        ]
    
    return Response({
        'message': f'Found {len(events)} events from database',
        'test_events': events
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def test_database(request):
    """Test endpoint to check database content"""
    from django.contrib.auth.models import User
    from meals.models import Meal, MealRecord
    from activities.models import Activity, ActivityRecord
    
    users = User.objects.all()
    meals = Meal.objects.all()
    activities = Activity.objects.all()
    meal_records = MealRecord.objects.all()
    activity_records = ActivityRecord.objects.all()
    
    return Response({
        'users_count': users.count(),
        'meals_count': meals.count(),
        'activities_count': activities.count(),
        'meal_records_count': meal_records.count(),
        'activity_records_count': activity_records.count(),
        'first_user': users.first().username if users.exists() else None,
        'first_meal': meals.first().name if meals.exists() else None,
        'first_activity': activities.first().name if activities.exists() else None,
    })
