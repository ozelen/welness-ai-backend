from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import json

from .models import HealthCalculator, Metric, MetricValue, ActivityLog
from .services import HealthCalculatorService, HealthMetricsService
from .forms import HealthCalculatorForm, MetricValueForm, ActivityLogForm


@login_required
def health_calculator_dashboard(request):
    """Main dashboard for health metrics - now shows metrics table"""
    user = request.user
    
    # Get favorite metrics first
    favorite_metrics = HealthMetricsService.get_user_favorites(user)
    
    # If user has no favorites, set up defaults
    if not favorite_metrics:
        HealthMetricsService.setup_default_favorites(user)
        favorite_metrics = HealthMetricsService.get_user_favorites(user)
    
    # Get all available metrics
    available_metrics = HealthMetricsService.get_available_metrics(user)
    
    # Get favorite metric IDs for UI
    favorite_metric_ids = [metric['id'] for metric in favorite_metrics]
    
    # Prepare metrics data
    metrics_data = []
    
    # First add favorite metrics
    for metric in favorite_metrics:
        metrics_data.append(get_metric_data(user, metric))
    
    # Then add other metrics
    for metric in available_metrics:
        if metric['id'] not in favorite_metric_ids:
            metrics_data.append(get_metric_data(user, metric))

    context = {
        'favorite_metrics': favorite_metrics,
        'metrics_data': metrics_data,
        'available_metrics': available_metrics,
        'favorite_metric_ids': favorite_metric_ids,
    }
    return render(request, 'metrics/dashboard.html', context)

def get_metric_data(user, metric):
    """Helper function to get metric data with current, previous, and target values"""
    current_value = None
    current_timestamp = None
    try:
        current_metric = Metric.objects.get(name=metric['name'], is_active=True)
        
        # For calculated metrics, evaluate the formula
        if current_metric.is_calculated and current_metric.calculation_formula:
            calculated_value = HealthMetricsService.get_calculated_value(user, current_metric)
            if calculated_value is not None:
                current_value = calculated_value
                current_timestamp = timezone.now()  # Use current time for calculated values
            else:
                print(f"Could not calculate value for {current_metric.name} with formula: {current_metric.calculation_formula}")
        else:
            # For regular metrics, get the latest measurement
            current_metric_value = MetricValue.objects.filter(
                user=user,
                metric=current_metric,
                measurement_type__in=['log', 'current', 'baseline']  # Only get actual measurements, not targets
            ).order_by('-timestamp').first()
            if current_metric_value:
                current_value = current_metric_value.value
                current_timestamp = current_metric_value.timestamp
    except Metric.DoesNotExist:
        pass

    previous_value = None
    week_ago = timezone.now() - timedelta(days=7)
    try:
        previous_metric_value = MetricValue.objects.filter(
            user=user,
            metric=current_metric,
            timestamp__lte=week_ago
        ).order_by('-timestamp').first()
        if previous_metric_value:
            previous_value = previous_metric_value.value
    except:
        pass

    target_value = None
    try:
        target_metric_value = MetricValue.objects.filter(
            user=user,
            metric=current_metric,
            measurement_type='target'
        ).order_by('-timestamp').first()
        if target_metric_value:
            target_value = target_metric_value.value
    except:
        pass

    return {
        'metric': metric,
        'current_value': current_value,
        'current_timestamp': current_timestamp,
        'previous_value': previous_value,
        'target_value': target_value,
    }

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    """Toggle favorite status for a metric"""
    try:
        data = json.loads(request.body)
        metric_id = data.get('metric_id')
        
        if not metric_id:
            return JsonResponse({'success': False, 'error': 'Metric ID is required'})
        
        result = HealthMetricsService.toggle_favorite(request.user, metric_id)
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def health_calculator_form(request):
    """Form to create/update health calculator"""
    user = request.user
    
    if request.method == 'POST':
        form = HealthCalculatorForm(request.POST)
        if form.is_valid():
            calculator = form.save(commit=False)
            calculator.user = user
            
            # Calculate all metrics and store them
            results = calculator.calculate_and_store_metrics()
            
            messages.success(request, 'Health calculations completed successfully!')
            return redirect('metrics:calculator_result', calculator_id=calculator.id)
    else:
        # Pre-populate with latest measurements if available
        latest_measurements = HealthMetricsService.get_latest_measurements(user)
        initial_data = {}
        
        if latest_measurements['weight_kg']:
            initial_data['weight_kg'] = latest_measurements['weight_kg']
        if latest_measurements['height_cm']:
            initial_data['height_cm'] = latest_measurements['height_cm']
        if latest_measurements['body_fat_percentage']:
            initial_data['body_fat_percentage'] = latest_measurements['body_fat_percentage']
        
        form = HealthCalculatorForm(initial=initial_data)
    
    context = {
        'form': form,
        'latest_measurements': HealthMetricsService.get_latest_measurements(user),
    }
    
    return render(request, 'metrics/calculator_form.html', context)


@login_required
def calculator_result(request, calculator_id):
    """Display health calculator results"""
    calculator = get_object_or_404(HealthCalculator, id=calculator_id, user=request.user)
    
    # Get calculated results
    calculated_results = calculator.get_calculated_results()
    
    # Get BMI category
    bmi_category = None
    if calculated_results.get('bmi'):
        bmi_category = HealthCalculatorService.get_bmi_category(calculated_results['bmi'])
    
    # Get recommendations based on results
    recommendations = get_health_recommendations(calculator, calculated_results)
    
    context = {
        'calculator': calculator,
        'calculated_results': calculated_results,
        'bmi_category': bmi_category,
        'recommendations': recommendations,
    }
    
    return render(request, 'metrics/calculator_result.html', context)


@login_required
def metric_values(request):
    """Manage metric values (measurements)"""
    user = request.user
    
    if request.method == 'POST':
        # Handle AJAX form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('X-CSRFToken'):
            try:
                metric_name = request.POST.get('metric_name')
                metric_type = request.POST.get('metric_type')
                metric_unit = request.POST.get('metric_unit')
                value = float(request.POST.get('value'))
                measurement_type = request.POST.get('measurement_type', 'log')
                source = request.POST.get('source', '')
                notes = request.POST.get('notes', '')
                
                # Check if this is a calculated metric
                is_calculated = request.POST.get('is_calculated', 'false').lower() == 'true'
                
                if is_calculated:
                    # For calculated metrics, don't store a value - it's computed dynamically
                    success_message = f'{metric_name} is a calculated metric. The value is computed automatically based on other measurements.'
                    metric_value = None
                elif measurement_type == 'target':
                    metric_value = HealthMetricsService.add_or_update_target(
                        user=user,
                        metric_name=metric_name,
                        target_value=value,
                        notes=notes
                    )
                    success_message = f'{metric_name} target updated successfully!'
                else:
                    metric_value = HealthMetricsService.add_metric_value(
                        user=user,
                        metric_name=metric_name,
                        value=value,
                        measurement_type=measurement_type,
                        notes=notes,
                        source=source
                    )
                    success_message = f'{metric_name} measurement added successfully!'
                
                response_data = {
                    'success': True,
                    'message': success_message,
                }
                
                if metric_value:
                    response_data['metric_value'] = metric_value.to_dict()
                
                return JsonResponse(response_data)
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
        else:
            # Handle regular form submission
            form = MetricValueForm(request.POST)
            if form.is_valid():
                metric_value = form.save(commit=False)
                metric_value.user = user
                metric_value.save()
                
                messages.success(request, 'Measurement added successfully!')
                return redirect('metrics:metric_values')
    else:
        form = MetricValueForm()
    
    # Get latest measurements for display
    latest_measurements = HealthMetricsService.get_latest_measurements(user)
    
    # Get available metrics for the form
    available_metrics = HealthMetricsService.get_available_metrics(user)
    
    context = {
        'form': form,
        'latest_measurements': latest_measurements,
        'available_metrics': available_metrics,
    }
    
    return render(request, 'metrics/metric_values.html', context)


@login_required
def activity_log(request):
    """Manage activity logs"""
    user = request.user
    
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = user
            activity.save()
            
            messages.success(request, 'Activity logged successfully!')
            return redirect('metrics:activity_log')
    else:
        form = ActivityLogForm()
    
    # Get activity history
    activities = ActivityLog.objects.filter(user=user).order_by('-activity_date', '-start_time')
    
    context = {
        'form': form,
        'activities': activities,
    }
    
    return render(request, 'metrics/activity_log.html', context)


@login_required
def measurement_history(request):
    """View measurement history with charts"""
    user = request.user
    
    # Get different measurement types
    weight_measurements = MetricValue.objects.filter(
        user=user, metric__name='Weight'
    ).order_by('timestamp').select_related('metric')[:30]
    
    body_fat_measurements = MetricValue.objects.filter(
        user=user, metric__name='Body Fat Percentage'
    ).order_by('timestamp').select_related('metric')[:30]
    
    bmi_measurements = MetricValue.objects.filter(
        user=user, metric__name='BMI'
    ).order_by('timestamp').select_related('metric')[:30]
    
    context = {
        'weight_measurements': weight_measurements,
        'body_fat_measurements': body_fat_measurements,
        'bmi_measurements': bmi_measurements,
    }
    
    return render(request, 'metrics/measurement_history.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def calculate_ajax(request):
    """AJAX endpoint for real-time calculations"""
    try:
        data = json.loads(request.body)
        
        weight_kg = float(data.get('weight_kg', 0))
        height_cm = float(data.get('height_cm', 0))
        body_fat_percentage = float(data.get('body_fat_percentage', 0))
        age_years = int(data.get('age_years', 0))
        gender = data.get('gender', 'male')
        activity_level = data.get('activity_level', 'moderately_active')
        
        # Calculate all metrics
        lbm = HealthCalculatorService.calculate_lbm(weight_kg, body_fat_percentage)
        bmr = HealthCalculatorService.calculate_bmr(weight_kg, height_cm, age_years, gender)
        tdee = HealthCalculatorService.calculate_tdee(bmr, activity_level)
        bmi = HealthCalculatorService.calculate_bmi(weight_kg, height_cm)
        bmi_category = HealthCalculatorService.get_bmi_category(bmi)
        body_fat_mass = HealthCalculatorService.calculate_body_fat_mass(weight_kg, body_fat_percentage)
        
        return JsonResponse({
            'success': True,
            'results': {
                'lbm_kg': round(lbm, 1) if lbm else None,
                'bmr_kcal': round(bmr, 0) if bmr else None,
                'tdee_kcal': round(tdee, 0) if tdee else None,
                'bmi': round(bmi, 1) if bmi else None,
                'bmi_category': bmi_category,
                'body_fat_mass_kg': round(body_fat_mass, 1) if body_fat_mass else None,
            }
        })
        
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def custom_metrics(request):
    """Manage custom metrics"""
    user = request.user
    
    if request.method == 'POST':
        # Handle custom metric creation
        metric_name = request.POST.get('name')
        metric_type = request.POST.get('type')
        unit = request.POST.get('unit')
        description = request.POST.get('description', '')
        
        if metric_name and metric_type and unit:
            try:
                metric = HealthMetricsService.create_custom_metric(
                    user=user,
                    name=metric_name,
                    type=metric_type,
                    unit=unit,
                    description=description
                )
                messages.success(request, f'Custom metric "{metric_name}" created successfully!')
                return redirect('metrics:custom_metrics')
            except Exception as e:
                messages.error(request, f'Error creating metric: {str(e)}')
    
    # Get user's custom metrics
    custom_metrics = Metric.objects.filter(
        is_custom=True, 
        created_by=user
    ).order_by('name')
    
    context = {
        'custom_metrics': custom_metrics,
    }
    
    return render(request, 'metrics/custom_metrics.html', context)


def get_health_recommendations(calculator, calculated_results):
    """Generate health recommendations based on calculator results"""
    recommendations = []
    
    bmi = calculated_results.get('bmi')
    if bmi:
        if bmi < 18.5:
            recommendations.append({
                'type': 'warning',
                'title': 'Underweight',
                'message': 'Consider increasing your caloric intake and focusing on muscle-building exercises.'
            })
        elif bmi > 30:
            recommendations.append({
                'type': 'warning',
                'title': 'High BMI',
                'message': 'Consider consulting with a healthcare provider about weight management strategies.'
            })
    
    body_fat_percentage = calculator.body_fat_percentage
    if body_fat_percentage:
        if body_fat_percentage > 25:
            recommendations.append({
                'type': 'info',
                'title': 'High Body Fat',
                'message': 'Consider incorporating more cardio and strength training to reduce body fat percentage.'
            })
        elif body_fat_percentage < 10:
            recommendations.append({
                'type': 'warning',
                'title': 'Low Body Fat',
                'message': 'Very low body fat can affect hormone levels. Consider consulting a healthcare provider.'
            })
    
    tdee_kcal = calculated_results.get('tdee_kcal')
    if tdee_kcal:
        recommendations.append({
            'type': 'success',
            'title': 'Daily Calorie Needs',
            'message': f'Your estimated daily calorie needs are {tdee_kcal:.0f} kcal for maintenance.'
        })
    
    return recommendations
