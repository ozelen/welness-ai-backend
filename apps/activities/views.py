from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Activity, ActivityRecord, ActivityType
from .forms import ActivityForm, ActivityRecordForm
from .services import ActivityService


@login_required
def activities_calendar_view(request):
    """Calendar view for activities (planned and logged)"""
    user = request.user
    
    # Get week parameter or default to current week
    week_param = request.GET.get('week')
    view_type = request.GET.get('view', 'week')  # week or day
    
    if week_param:
        try:
            # Parse week parameter (format: YYYY-WW)
            year, week = week_param.split('-')
            year, week = int(year), int(week)
            # Get the first day of the week
            start_date = date.fromisocalendar(year, week, 1)
        except (ValueError, TypeError):
            start_date = timezone.now().date()
    else:
        start_date = timezone.now().date()
    
    # Calculate week boundaries
    week_start = start_date - timedelta(days=start_date.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get activities for the week
    week_activities = {}
    week_records = {}
    
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        
        # Get planned activities for this day
        activities = Activity.objects.filter(
            user=user,
            date=current_date
        ).order_by('created_at')
        
        # Get logged activities for this day
        records = ActivityRecord.objects.filter(
            user=user,
            date=current_date
        ).order_by('created_at')
        
        week_activities[current_date] = activities
        week_records[current_date] = records
    
    # Calculate weekly totals
    week_totals = {
        'planned_hours': 0,
        'actual_hours': 0,
        'planned_calories': 0,
        'actual_calories': 0,
    }
    
    for current_date in week_activities:
        # Sum planned hours
        for activity in week_activities[current_date]:
            week_totals['planned_hours'] += activity.duration_hours
        
        # Sum actual hours
        for record in week_records[current_date]:
            week_totals['actual_hours'] += record.duration_hours
    
    # Calculate calories (this would need weight from metrics app)
    weight_kg = 70.0  # Default weight, should be fetched from metrics
    for current_date in week_activities:
        for activity in week_activities[current_date]:
            deficit = ActivityService.get_activity_deficit(activity.activity_type)
            week_totals['planned_calories'] += deficit * weight_kg * activity.duration_hours
        
        for record in week_records[current_date]:
            deficit = ActivityService.get_activity_deficit(record.activity_type)
            week_totals['actual_calories'] += deficit * weight_kg * record.duration_hours
    
    # Round totals
    week_totals = {k: round(v, 1) for k, v in week_totals.items()}
    
    context = {
        'week_start': week_start,
        'week_end': week_end,
        'week_activities': week_activities,
        'week_records': week_records,
        'week_totals': week_totals,
        'view_type': view_type,
        'activity_types': ActivityType.objects.filter(is_active=True).order_by('category', 'display_name'),
    }
    
    if view_type == 'day':
        # For day view, get the specific day
        day_param = request.GET.get('day')
        if day_param:
            try:
                selected_date = date.fromisoformat(day_param)
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()
        
        context['selected_date'] = selected_date
        context['day_activities'] = week_activities.get(selected_date, [])
        context['day_records'] = week_records.get(selected_date, [])
        
        return render(request, 'activities/calendar_day.html', context)
    
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
        data = json.loads(request.body)
        form = ActivityForm(data)
        
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
def create_activity_record(request):
    """Create a new activity record (logged activity)"""
    try:
        data = json.loads(request.body)
        form = ActivityRecordForm(data)
        
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            
            return JsonResponse({
                'success': True,
                'record': record.to_dict()
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
    
    # Get recent activities and records
    recent_activities = Activity.objects.filter(user=user).order_by('-date', '-created_at')[:10]
    recent_records = ActivityRecord.objects.filter(user=user).order_by('-date', '-created_at')[:10]
    
    context = {
        'recent_activities': recent_activities,
        'recent_records': recent_records,
        'activity_types': ActivityType.objects.filter(is_active=True).order_by('category', 'display_name'),
    }
    
    return render(request, 'activities/activities.html', context)
