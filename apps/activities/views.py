from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Activity, ActivityRecord, ActivityType
from .forms import ActivityForm, ActivityRecordForm
from .services import ActivityService
from .models import Exercise
from .forms import ExerciseForm
from .models import ActivityExercise


@login_required
def activities_calendar_view(request):
    """Calendar view for activities"""
    # Get week parameter from URL
    week_param = request.GET.get('week')
    
    if week_param:
        try:
            # Parse week parameter (format: YYYY-WW)
            year, week = week_param.split('-')
            year, week = int(year), int(week)
            # Get the first day of the week
            from datetime import datetime, timedelta
            january_first = datetime(year, 1, 1)
            days_since_january_first = (week - 1) * 7
            start_of_week = january_first + timedelta(days=days_since_january_first)
            # Adjust to Monday
            while start_of_week.weekday() != 0:  # Monday is 0
                start_of_week -= timedelta(days=1)
        except (ValueError, TypeError):
            start_of_week = timezone.now().date()
    else:
        start_of_week = timezone.now().date()
    
    # Calculate end of week
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get activities for the week
    activities = Activity.objects.filter(
        user=request.user,
        start_date__gte=start_of_week,
        start_date__lte=end_of_week
    ).order_by('start_date', 'start_time')
    
    # Get activity records for the week
    activity_records = ActivityRecord.objects.filter(
        user=request.user,
        date__gte=start_of_week,
        date__lte=end_of_week
    ).order_by('date', 'start_time')
    
    # Group activities by day
    activities_by_day = {}
    for day in range(7):
        current_date = start_of_week + timedelta(days=day)
        activities_by_day[current_date] = {
            'activities': [],
            'records': [],
            'total_calories': 0,
            'total_duration': 0
        }
    
    # Populate activities
    for activity in activities:
        day_data = activities_by_day.get(activity.start_date, {
            'activities': [],
            'records': [],
            'total_calories': 0,
            'total_duration': 0
        })
        day_data['activities'].append(activity)
        if activity.calories_burned:
            day_data['total_calories'] += activity.calories_burned
        day_data['total_duration'] += activity.duration_hours
        activities_by_day[activity.start_date] = day_data
    
    # Populate activity records
    for record in activity_records:
        day_data = activities_by_day.get(record.date, {
            'activities': [],
            'records': [],
            'total_calories': 0,
            'total_duration': 0
        })
        day_data['records'].append(record)
        if record.get_calories_burned():
            day_data['total_calories'] += record.get_calories_burned()
        day_data['total_duration'] += record.get_duration_hours()
        activities_by_day[record.date] = day_data
    
    # Calculate week totals
    week_totals = {
        'total_calories': sum(day['total_calories'] for day in activities_by_day.values()),
        'total_duration': sum(day['total_duration'] for day in activities_by_day.values()),
        'total_activities': sum(len(day['activities']) for day in activities_by_day.values()),
        'total_records': sum(len(day['records']) for day in activities_by_day.values())
    }
    
    # Calculate navigation weeks
    previous_week = (start_of_week - timedelta(days=7)).strftime('%Y-%W')
    next_week = (start_of_week + timedelta(days=7)).strftime('%Y-%W')
    
    context = {
        'activities_by_day': activities_by_day,
        'week_totals': week_totals,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'current_week': f"{start_of_week.year}-{start_of_week.isocalendar()[1]:02d}",
        'previous_week': previous_week,
        'next_week': next_week,
        'today': timezone.now().date(),
        'activity_types': ActivityType.objects.filter(is_active=True),
        'user_activities': Activity.objects.filter(user=request.user, is_scheduled=True),
    }
    
    return render(request, 'activities/calendar.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_activity_completion(request, activity_id):
    """Toggle completion status of a planned activity"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        activity.is_completed = not activity.is_completed
        activity.save()
        
        return JsonResponse({
            'success': True,
            'is_completed': activity.is_completed
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def create_activity(request):
    """Create a new planned activity"""
    try:
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            
            return JsonResponse({
                'success': True,
                'activity': activity.to_dict()
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def update_activity(request, activity_id):
    """Update an existing activity"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        form = ActivityForm(request.POST, instance=activity)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'activity': activity.to_dict()
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def create_activity_record(request):
    """Log an activity (planned or unplanned)"""
    try:
        form = ActivityRecordForm(request.POST, user=request.user)
        if form.is_valid():
            activity_record = form.save(commit=False)
            activity_record.user = request.user
            
            # Handle unplanned activities
            if not activity_record.activity:
                activity_record.activity_name = form.cleaned_data.get('activity_name')
                activity_record.activity_type_name = form.cleaned_data.get('activity_type_name')
                activity_record.duration_hours = form.cleaned_data.get('duration_hours')
            
            activity_record.save()
            
            return JsonResponse({
                'success': True,
                'activity_record': activity_record.to_dict()
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["DELETE"])
def delete_activity(request, activity_id):
    """Delete a planned activity"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        activity.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["DELETE"])
def delete_activity_record(request, record_id):
    """Delete an activity record"""
    try:
        record = get_object_or_404(ActivityRecord, id=record_id, user=request.user)
        record.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def activities_management_page(request):
    """Management page for activities"""
    user = request.user
    
    # Get all activities (both planned and completed)
    activities = Activity.objects.filter(user=user).order_by('-start_date', '-created_at')
    
    # Get all activity types for filtering
    activity_types = ActivityType.objects.filter(is_active=True).order_by('category', 'display_name')
    
    # Get selected activity type filter
    selected_activity_type_id = request.GET.get('activity_type')
    if selected_activity_type_id:
        activities = activities.filter(activity_type_id=selected_activity_type_id)
    
    context = {
        'activities': activities,
        'activity_types': activity_types,
        'selected_activity_type_id': selected_activity_type_id,
    }
    
    return render(request, 'activities/activities.html', context)


@login_required
@require_http_methods(["POST"])
def create_exercise(request):
    """Create a new exercise"""
    try:
        form = ExerciseForm(request.POST)
        
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.created_by = request.user
            exercise.is_personal = True
            exercise.save()
            
            return JsonResponse({
                'success': True,
                'exercise': exercise.to_dict()
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["DELETE"])
def delete_exercise(request, exercise_id):
    """Delete an exercise (only personal exercises)"""
    try:
        exercise = get_object_or_404(Exercise, id=exercise_id, created_by=request.user, is_personal=True)
        exercise.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["POST"])
def create_activity_exercise(request):
    """Add an exercise to an activity"""
    try:
        activity_id = request.POST.get('activity_id')
        exercise_name = request.POST.get('exercise_name')
        notes = request.POST.get('notes', '').strip()
        
        # Get the activity
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        
        # Get or create the exercise
        exercise, created = Exercise.objects.get_or_create(
            name=exercise_name,
            defaults={
                'created_by': request.user,
                'is_personal': True,
                'category': 'Custom'
            }
        )
        
        # Parse notes to extract structured data according to activity type schema
        details = {}
        if notes and activity.activity_type.exercise_schema:
            # Use the activity type's schema to guide parsing
            schema = activity.activity_type.exercise_schema
            import re
            
            # Extract data based on schema properties
            for field_name, field_config in schema.get('properties', {}).items():
                if field_name in ['duration_minutes', 'sets', 'reps']:
                    # Look for numeric patterns
                    pattern = rf'(\d+)\s*{field_name.replace("_", " ")}'
                    match = re.search(pattern, notes, re.IGNORECASE)
                    if match:
                        details[field_name] = int(match.group(1))
                
                elif field_name in ['weight_kg', 'distance_km']:
                    # Look for weight/distance patterns
                    if field_name == 'weight_kg':
                        pattern = r'(\d+(?:\.\d+)?)\s*(?:kg|kilos?|pounds?|lbs?)'
                    else:  # distance_km
                        pattern = r'(\d+(?:\.\d+)?)\s*(?:km|kilometers?|miles?)'
                    
                    match = re.search(pattern, notes, re.IGNORECASE)
                    if match:
                        details[field_name] = float(match.group(1))
        
        # Set defaults from schema if not found in notes
        if activity.activity_type.exercise_schema:
            schema = activity.activity_type.exercise_schema
            for field_name, field_config in schema.get('properties', {}).items():
                if field_name not in details and 'default' in field_config:
                    details[field_name] = field_config['default']
        
        # Create the activity exercise
        activity_exercise = ActivityExercise.objects.create(
            activity=activity,
            exercise=exercise,
            notes=notes if notes else None,
            details=details,
            order=activity.exercises.count()
        )
        
        return JsonResponse({
            'success': True,
            'activity_exercise': activity_exercise.to_dict()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["DELETE"])
def delete_activity_exercise(request, exercise_id):
    """Delete an exercise from an activity"""
    try:
        activity_exercise = get_object_or_404(ActivityExercise, id=exercise_id, activity__user=request.user)
        activity_exercise.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def exercise_suggestions(request):
    """Get exercise suggestions for autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search for exercises that match the query
    exercises = Exercise.objects.filter(
        name__icontains=query,
        is_active=True
    ).order_by('name')[:10]
    
    suggestions = [exercise.to_dict() for exercise in exercises]
    
    return JsonResponse({'suggestions': suggestions})


@login_required
def get_activity_data(request, activity_id):
    """Get activity data for editing/scheduling"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        return JsonResponse({
            'success': True,
            'activity': {
                'id': activity.id,
                'name': activity.name,
                'activity_type': activity.activity_type.id,
                'duration_hours': activity.duration_hours,
                'is_scheduled': activity.is_scheduled,
                'start_date': activity.start_date.isoformat() if activity.start_date else None,
                'start_time': activity.start_time.isoformat() if activity.start_time else None,
                'recurrence_type': activity.recurrence_type,
                'recurrence_until': activity.recurrence_until.isoformat() if activity.recurrence_until else None,
                'recurrence_days': activity.recurrence_days,
                'notes': activity.notes,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["POST"])
def schedule_activity(request):
    """Schedule an existing activity"""
    try:
        activity_id = request.POST.get('activity_id')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        recurrence_type = request.POST.get('recurrence_type', 'none')
        recurrence_until = request.POST.get('recurrence_until')
        recurrence_days = request.POST.get('recurrence_days', '').strip()
        
        # Get the activity
        activity = get_object_or_404(Activity, id=activity_id, user=request.user)
        
        # Update the activity with scheduling information
        activity.is_scheduled = True
        if start_date:
            activity.start_date = start_date  # Django will handle string to date conversion
        if start_time:
            activity.start_time = start_time  # Django will handle string to time conversion
        activity.recurrence_type = recurrence_type
        if recurrence_until and recurrence_type != 'none':
            activity.recurrence_until = recurrence_until  # Django will handle string to date conversion
        if recurrence_type == 'custom':
            activity.recurrence_days = recurrence_days
        
        activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Activity scheduled successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
