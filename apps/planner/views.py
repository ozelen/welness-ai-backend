from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from meals.models import Meal, MealRecord, Diet
from activities.models import Activity, ActivityRecord
from user_auth.models import UserProfile
from metrics.models import Metric, MetricValue


@login_required
def calendar_view(request):
    user = request.user
    week_param = request.GET.get('week')
    view_type = request.GET.get('view', 'week')
    selected_date = request.GET.get('date')
    
    # Handle week parameter
    if week_param:
        try:
            year, week = map(int, week_param.split('-'))
            start_date = date.fromisocalendar(year, week, 1)
        except Exception:
            start_date = timezone.now().date()
    else:
        start_date = timezone.now().date()
    
    # Handle day view
    if view_type == 'day' and selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
        except:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    week_start = start_date - timedelta(days=start_date.weekday())
    week_days = [week_start + timedelta(days=i) for i in range(7)]
    week_end = week_days[-1]
    
    # Get scheduled meals for the week (including recurrent meals)
    scheduled_meals = Meal.objects.filter(
        diet__user=user,
        is_scheduled=True
    ).select_related('diet').prefetch_related('mealingredient_set__ingredient')
    
    # Get scheduled activities for the week (including recurrent activities)
    scheduled_activities = Activity.objects.filter(
        user=user,
        is_scheduled=True
    ).select_related('activity_type')
    
    # Get meal records for the week (completed meals and unplanned meals)
    meal_records = MealRecord.objects.filter(
        user=user,
        timestamp__date__gte=week_start,
        timestamp__date__lte=week_end
    ).order_by('timestamp')
    
    # Get activity records for the week (completed activities and unplanned activities)
    activity_records = ActivityRecord.objects.filter(
        user=user,
        date__gte=week_start,
        date__lte=week_end
    ).order_by('date', 'start_time')
    
    # Organize events by day
    events_by_day = {d: [] for d in week_days}
    
    # Create lookup sets for completed meal and activity IDs by date
    completed_meal_ids_by_day = {}
    completed_activity_ids_by_day = {}
    
    for day in week_days:
        completed_meal_ids_by_day[day] = set()
        completed_activity_ids_by_day[day] = set()
    
    # Populate completed lookup sets
    for record in meal_records:
        if record.meal:  # Only for planned meals that were logged
            completed_meal_ids_by_day[record.timestamp.date()].add(record.meal.id)
    
    for record in activity_records:
        if record.activity:  # Only for planned activities that were logged
            completed_activity_ids_by_day[record.date].add(record.activity.id)
    
    # Process scheduled meals with recurrence logic
    for meal in scheduled_meals:
        # Check if meal has a valid date range
        meal_start = meal.start_date or week_start
        meal_end = meal.end_date or meal.recurrence_until
        
        # Skip if meal ends before this week starts
        if meal_end and meal_end < week_start:
            continue
            
        # Skip if meal starts after this week ends
        if meal_start and meal_start > week_end:
            continue
            
        if meal.recurrence_type == 'none':
            # Single occurrence - check if it's in this week
            if meal.start_date and week_start <= meal.start_date <= week_end:
                is_completed = meal.id in completed_meal_ids_by_day.get(meal.start_date, set())
                day_events = events_by_day.get(meal.start_date, [])
                day_events.append({
                    'type': 'meal',
                    'object': meal,
                    'title': meal.name,
                    'time': meal.start_time,
                    'duration': meal.duration_minutes or 30,
                    'category': 'meal',
                    'color': 'blue',
                    'is_completed': is_completed,
                    'nutrition': {
                        'calories': meal.get_total_calories(),
                        'proteins': 0,  # TODO: Add protein calculation
                        'carbs': 0,     # TODO: Add carb calculation
                        'fats': 0,      # TODO: Add fat calculation
                    },
                })
                events_by_day[meal.start_date] = day_events
        elif meal.recurrence_type == 'daily':
            # Daily recurrence - add to every day in the week within the date range
            for i in range(7):
                day_date = week_start + timedelta(days=i)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    is_completed = meal.id in completed_meal_ids_by_day.get(day_date, set())
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'meal',
                        'object': meal,
                        'title': meal.name,
                        'time': meal.start_time,
                        'duration': meal.duration_minutes or 30,
                        'category': 'meal',
                        'color': 'blue',
                        'is_completed': is_completed,
                        'nutrition': {
                            'calories': meal.get_total_calories(),
                            'proteins': 0,
                            'carbs': 0,
                            'fats': 0,
                        },
                    })
                    events_by_day[day_date] = day_events
        elif meal.recurrence_type == 'weekly':
            # Weekly recurrence - add to the same day of the week
            if meal.start_date:
                # Find the day of week (0=Monday, 6=Sunday)
                meal_day_of_week = meal.start_date.weekday()
                # Get the corresponding day in the current week
                day_date = week_start + timedelta(days=meal_day_of_week)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'meal',
                        'object': meal,
                        'title': meal.name,
                        'time': meal.start_time,
                        'duration': meal.duration_minutes or 30,
                        'category': 'meal',
                        'color': 'blue',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'nutrition': {
                            'calories': meal.get_total_calories(),
                            'proteins': 0,
                            'carbs': 0,
                            'fats': 0,
                        },
                    })
                    events_by_day[day_date] = day_events
        elif meal.recurrence_type == 'weekday':
            # Weekdays (Mon-Fri) - add to Monday through Friday
            for i in range(5):  # Monday to Friday
                day_date = week_start + timedelta(days=i)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'meal',
                        'object': meal,
                        'title': meal.name,
                        'time': meal.start_time,
                        'duration': meal.duration_minutes or 30,
                        'category': 'meal',
                        'color': 'blue',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'nutrition': {
                            'calories': meal.get_total_calories(),
                            'proteins': 0,
                            'carbs': 0,
                            'fats': 0,
                        },
                    })
                    events_by_day[day_date] = day_events
        elif meal.recurrence_type == 'weekend':
            # Weekends (Sat-Sun) - add to Saturday and Sunday
            for i in range(5, 7):  # Saturday and Sunday
                day_date = week_start + timedelta(days=i)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'meal',
                        'object': meal,
                        'title': meal.name,
                        'time': meal.start_time,
                        'duration': meal.duration_minutes or 30,
                        'category': 'meal',
                        'color': 'blue',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'nutrition': {
                            'calories': meal.get_total_calories(),
                            'proteins': 0,
                            'carbs': 0,
                            'fats': 0,
                        },
                    })
                    events_by_day[day_date] = day_events
        elif meal.recurrence_type == 'custom' and meal.recurrence_days:
            # Custom days - parse recurrence_days and add to specified days
            day_mapping = {
                'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 
                'fri': 4, 'sat': 5, 'sun': 6
            }
            custom_days = []
            for day in meal.recurrence_days.lower().split(','):
                day = day.strip()
                if day in day_mapping:
                    custom_days.append(day_mapping[day])
            
            for day_index in custom_days:
                day_date = week_start + timedelta(days=day_index)
                if day_date >= meal_start and (not meal_end or day_date <= meal_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'meal',
                        'object': meal,
                        'title': meal.name,
                        'time': meal.start_time,
                        'duration': meal.duration_minutes or 30,
                        'category': 'meal',
                        'color': 'blue',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'nutrition': {
                            'calories': meal.get_total_calories(),
                            'proteins': 0,
                            'carbs': 0,
                            'fats': 0,
                        },
                    })
                    events_by_day[day_date] = day_events
    
    # Process scheduled activities with recurrence logic
    for activity in scheduled_activities:
        # Check if activity has a valid date range
        activity_start = activity.start_date or week_start
        activity_end = activity.end_date or activity.recurrence_until
        
        # Skip if activity ends before this week starts
        if activity_end and activity_end < week_start:
            continue
            
        # Skip if activity starts after this week ends
        if activity_start and activity_start > week_end:
            continue
            
        if activity.recurrence_type == 'none':
            # Single occurrence - check if it's in this week
            if activity.start_date and week_start <= activity.start_date <= week_end:
                is_completed = activity.id in completed_activity_ids_by_day.get(activity.start_date, set())
                day_events = events_by_day.get(activity.start_date, [])
                day_events.append({
                    'type': 'activity',
                    'object': activity,
                    'title': activity.name or activity.activity_type.display_name,
                    'time': activity.start_time,
                    'duration': int(activity.duration_hours * 60),
                    'category': 'activity',
                    'color': 'purple',
                    'is_completed': is_completed,
                    'calories_burned': activity.calories_burned,
                })
                events_by_day[activity.start_date] = day_events
        elif activity.recurrence_type == 'daily':
            # Daily recurrence - add to every day in the week within the date range
            for i in range(7):
                day_date = week_start + timedelta(days=i)
                if day_date >= activity_start and (not activity_end or day_date <= activity_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'activity',
                        'object': activity,
                        'title': activity.name or activity.activity_type.display_name,
                        'time': activity.start_time,
                        'duration': int(activity.duration_hours * 60),
                        'category': 'activity',
                        'color': 'purple',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'calories_burned': activity.calories_burned,
                    })
                    events_by_day[day_date] = day_events
        elif activity.recurrence_type == 'weekly':
            # Weekly recurrence - add to the same day of the week
            if activity.start_date:
                # Find the day of week (0=Monday, 6=Sunday)
                activity_day_of_week = activity.start_date.weekday()
                # Get the corresponding day in the current week
                day_date = week_start + timedelta(days=activity_day_of_week)
                if day_date >= activity_start and (not activity_end or day_date <= activity_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'activity',
                        'object': activity,
                        'title': activity.name or activity.activity_type.display_name,
                        'time': activity.start_time,
                        'duration': int(activity.duration_hours * 60),
                        'category': 'activity',
                        'color': 'purple',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'calories_burned': activity.calories_burned,
                    })
                    events_by_day[day_date] = day_events
        elif activity.recurrence_type == 'weekday':
            # Weekdays (Mon-Fri) - add to Monday through Friday
            for i in range(5):  # Monday to Friday
                day_date = week_start + timedelta(days=i)
                if day_date >= activity_start and (not activity_end or day_date <= activity_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'activity',
                        'object': activity,
                        'title': activity.name or activity.activity_type.display_name,
                        'time': activity.start_time,
                        'duration': int(activity.duration_hours * 60),
                        'category': 'activity',
                        'color': 'purple',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'calories_burned': activity.calories_burned,
                    })
                    events_by_day[day_date] = day_events
        elif activity.recurrence_type == 'weekend':
            # Weekends (Sat-Sun) - add to Saturday and Sunday
            for i in range(5, 7):  # Saturday and Sunday
                day_date = week_start + timedelta(days=i)
                if day_date >= activity_start and (not activity_end or day_date <= activity_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'activity',
                        'object': activity,
                        'title': activity.name or activity.activity_type.display_name,
                        'time': activity.start_time,
                        'duration': int(activity.duration_hours * 60),
                        'category': 'activity',
                        'color': 'purple',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'calories_burned': activity.calories_burned,
                    })
                    events_by_day[day_date] = day_events
        elif activity.recurrence_type == 'custom' and activity.recurrence_days:
            # Custom days - parse recurrence_days and add to specified days
            day_mapping = {
                'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 
                'fri': 4, 'sat': 5, 'sun': 6
            }
            custom_days = []
            for day in activity.recurrence_days.lower().split(','):
                day = day.strip()
                if day in day_mapping:
                    custom_days.append(day_mapping[day])
            
            for day_index in custom_days:
                day_date = week_start + timedelta(days=day_index)
                if day_date >= activity_start and (not activity_end or day_date <= activity_end):
                    day_events = events_by_day.get(day_date, [])
                    day_events.append({
                        'type': 'activity',
                        'object': activity,
                        'title': activity.name or activity.activity_type.display_name,
                        'time': activity.start_time,
                        'duration': int(activity.duration_hours * 60),
                        'category': 'activity',
                        'color': 'purple',
                        'is_completed': meal.id in completed_meal_ids_by_day.get(day_date, set()),
                        'calories_burned': activity.calories_burned,
                    })
                    events_by_day[day_date] = day_events
    
    # Add meal records (only unplanned meals - planned meals are shown as completed events above)
    for record in meal_records:
        if not record.meal:  # Only show unplanned meals as separate records
            day_events = events_by_day.get(record.timestamp.date(), [])
            day_events.append({
                'type': 'meal_record',
                'object': record,
                'title': record.meal_name,
                'time': record.timestamp.time(),
                'duration': 30,  # Default duration for logged meals
                'category': 'meal_logged',
                'color': 'green',
                'is_completed': True,
                'nutrition': {
                    'calories': record.calories or 0,
                    'proteins': record.proteins or 0,
                    'carbs': record.carbs or 0,
                    'fats': record.fats or 0,
                },
            })
            events_by_day[record.timestamp.date()] = day_events
    
    # Add activity records (only unplanned activities - planned activities are shown as completed events above)
    for record in activity_records:
        if not record.activity:  # Only show unplanned activities as separate records
            day_events = events_by_day.get(record.date, [])
            day_events.append({
                'type': 'activity_record',
                'object': record,
                'title': record.activity_name,
                'time': record.start_time,
                'duration': int(record.get_duration_hours() * 60),
                'category': 'activity_logged',
                'color': 'orange',
                'is_completed': True,
                'calories_burned': record.get_calories_burned(),
            })
            events_by_day[record.date] = day_events
    
    # Sort events by time within each day
    for day in events_by_day:
        events_by_day[day].sort(key=lambda x: x['time'] or timezone.now().time())
    
    # Calculate week totals
    week_totals = {
        'calories_in': sum(
            event.get('nutrition', {}).get('calories', 0) 
            for events in events_by_day.values() 
            for event in events 
            if event['type'] in ['meal_record']
        ),
        'calories_out': sum(
            event.get('calories_burned', 0) 
            for events in events_by_day.values() 
            for event in events 
            if event['type'] in ['activity_record']
        ),
        'proteins': sum(
            event.get('nutrition', {}).get('proteins', 0) 
            for events in events_by_day.values() 
            for event in events 
            if event['type'] in ['meal_record']
        ),
        'carbs': sum(
            event.get('nutrition', {}).get('carbs', 0) 
            for events in events_by_day.values() 
            for event in events 
            if event['type'] in ['meal_record']
        ),
        'fats': sum(
            event.get('nutrition', {}).get('fats', 0) 
            for events in events_by_day.values() 
            for event in events 
            if event['type'] in ['meal_record']
        ),
        'meals_planned': sum(1 for events in events_by_day.values() for event in events if event['type'] == 'meal'),
        'meals_logged': len(meal_records),
        'activities_planned': sum(1 for events in events_by_day.values() for event in events if event['type'] == 'activity'),
        'activities_logged': len(activity_records),
    }
    
    # Get user targets from active diet
    try:
        active_diet = Diet.objects.filter(user=user, is_active=True).first()
        if active_diet:
            weekly_targets = {
                'calories': active_diet.day_calories_kcal * 7,
                'proteins': active_diet.day_proteins_g * 7,
                'carbs': active_diet.day_carbohydrates_g * 7,
                'fats': active_diet.day_fats_g * 7,
            }
        else:
            weekly_targets = {'calories': 0, 'proteins': 0, 'carbs': 0, 'fats': 0}
    except Exception:
        weekly_targets = {'calories': 0, 'proteins': 0, 'carbs': 0, 'fats': 0}
    
    # Calculate percentages
    week_percentages = {}
    for nutrient in ['calories', 'proteins', 'carbs', 'fats']:
        target = weekly_targets.get(nutrient, 0)
        actual = week_totals.get(nutrient, 0)
        if target > 0:
            week_percentages[nutrient] = (actual / target) * 100
        else:
            week_percentages[nutrient] = 0
    
    # Navigation parameters
    current_week_param = f"{week_start.year}-{week_start.isocalendar()[1]:02d}"
    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)
    prev_week_param = f"{prev_week.year}-{prev_week.isocalendar()[1]:02d}"
    next_week_param = f"{next_week.year}-{next_week.isocalendar()[1]:02d}"
    
    # Define time grid parameters
    start_hour = 6  # Calendar starts at 6:00 AM
    end_hour = 22   # Calendar ends at 10:00 PM
    hours = list(range(start_hour, end_hour + 1))
    
    context = {
        'week_start': week_start,
        'week_end': week_end,
        'week_days': week_days,
        'events_by_day': events_by_day,
        'week_totals': week_totals,
        'weekly_targets': weekly_targets,
        'week_percentages': week_percentages,
        'current_week_param': current_week_param,
        'prev_week_param': prev_week_param,
        'next_week_param': next_week_param,
        'view_type': view_type,
        'selected_date': selected_date,
        'current_date': timezone.now().date(),
        'today': timezone.now().date(),
        'hours': hours,
        'start_hour': start_hour,
        'end_hour': end_hour,
    }
    return render(request, 'planner/calendar.html', context)

@login_required
def log_meal(request):
    """Log a meal for a specific date"""
    if request.method == 'POST':
        try:
            meal_id = request.POST.get('meal_id')
            date_str = request.POST.get('date')
            meal_name = request.POST.get('meal_name')
            calories = float(request.POST.get('calories', 0))
            proteins = float(request.POST.get('proteins', 0))
            carbs = float(request.POST.get('carbs', 0))
            fats = float(request.POST.get('fats', 0))
            notes = request.POST.get('notes', '')
            
            # Create meal record
            meal_record = MealRecord.objects.create(
                user=request.user,
                meal_id=meal_id if meal_id else None,
                meal_name=meal_name,
                calories=calories,
                proteins=proteins,
                carbs=carbs,
                fats=fats,
                notes=notes,
                timestamp=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Meal logged successfully',
                'record_id': meal_record.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def log_activity(request):
    """Log an activity for a specific date"""
    if request.method == 'POST':
        try:
            activity_id = request.POST.get('activity_id')
            date_str = request.POST.get('date')
            activity_name = request.POST.get('activity_name')
            duration_hours = float(request.POST.get('duration_hours', 0))
            calories_burned = float(request.POST.get('calories_burned', 0))
            notes = request.POST.get('notes', '')
            
            # Create activity record
            activity_record = ActivityRecord.objects.create(
                user=request.user,
                activity_id=activity_id if activity_id else None,
                activity_name=activity_name,
                duration_hours=duration_hours,
                notes=notes,
                date=date.fromisoformat(date_str) if date_str else timezone.now().date()
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Activity logged successfully',
                'record_id': activity_record.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
