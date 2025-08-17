from typing import Optional, Dict, Any, List
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import HealthCalculator, Metric, MetricValue, ActivityLog, UserMetricFavorite
from django.db import models


class HealthMetricsService:
    """Service for managing health metrics and measurements"""
    
    @staticmethod
    def get_latest_measurements(user: User) -> Dict[str, Any]:
        """Get the latest measurement for each metric"""
        latest_measurements = {}
        
        # Get all active metrics
        metrics = Metric.objects.filter(is_active=True)
        
        for metric in metrics:
            key = metric.name.lower().replace(' ', '_')
            try:
                latest_value = MetricValue.objects.filter(
                    user=user,
                    metric=metric
                ).order_by('-timestamp').first()
                
                if latest_value:
                    latest_measurements[key] = {
                        'value': float(latest_value.value),
                        'timestamp': latest_value.timestamp,
                        'measurement_type': latest_value.measurement_type,
                        'source': latest_value.source,
                        'notes': latest_value.notes
                    }
                else:
                    latest_measurements[key] = None
            except MetricValue.DoesNotExist:
                latest_measurements[key] = None
        
        return latest_measurements
    
    @staticmethod
    def create_health_calculator_from_measurements(user: User, gender: str, activity_level: str = 'moderately_active', activity_hours_per_week: float = 0, notes: str = "") -> HealthCalculator:
        """Create a health calculator instance using the latest measurements"""
        latest_measurements = HealthMetricsService.get_latest_measurements(user)
        
        calculator = HealthCalculator.objects.create(
            user=user,
            weight_kg=latest_measurements.get('weight_kg', 0),
            height_cm=latest_measurements.get('height_cm', 0),
            body_fat_percentage=latest_measurements.get('body_fat_percentage', 0),
            gender=gender,
            activity_level=activity_level,
            activity_hours_per_week=activity_hours_per_week,
            notes=notes
        )
        
        # Calculate all metrics
        calculator.calculate_all()
        
        return calculator
    
    @staticmethod
    def get_measurement_history(user: User, metric_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get measurement history for a specific metric"""
        try:
            metric = Metric.objects.get(name=metric_name, is_active=True)
        except Metric.DoesNotExist:
            return []
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        values = MetricValue.objects.filter(
            user=user,
            metric=metric,
            timestamp__gte=cutoff_date
        ).order_by('timestamp')
        
        return [
            {
                'timestamp': value.timestamp.isoformat(),
                'value': value.value,
                'unit': metric.unit,
                'measurement_type': value.measurement_type,
                'status': value.status,
                'notes': value.notes,
                'source': value.source
            }
            for value in values
        ]
    
    @staticmethod
    def get_activity_summary(user: User, days: int = 7) -> Dict[str, Any]:
        """Get activity summary for the specified number of days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        activities = ActivityLog.objects.filter(
            user=user,
            activity_date__gte=cutoff_date.date()
        )
        
        total_activities = activities.count()
        total_duration_minutes = sum(activity.duration_minutes for activity in activities)
        total_calories_burned = sum(activity.calories_burned or 0 for activity in activities)
        
        # Group by activity type
        activity_types = {}
        for activity in activities:
            activity_type = activity.get_activity_type_display()
            if activity_type not in activity_types:
                activity_types[activity_type] = {
                    'count': 0,
                    'total_duration': 0,
                    'total_calories': 0
                }
            activity_types[activity_type]['count'] += 1
            activity_types[activity_type]['total_duration'] += activity.duration_minutes
            activity_types[activity_type]['total_calories'] += activity.calories_burned or 0
        
        return {
            'total_activities': total_activities,
            'total_duration_minutes': total_duration_minutes,
            'total_calories_burned': total_calories_burned,
            'activity_types': activity_types,
            'period_days': days
        }
    
    @staticmethod
    def get_lab_results_summary(user: User, days: int = 365) -> Dict[str, Any]:
        """Get lab results summary for the specified number of days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        lab_results = MetricValue.objects.filter(
            user=user,
            metric__type='lab_result',
            timestamp__gte=cutoff_date
        ).select_related('metric')
        
        # Group by metric
        results_by_metric = {}
        for result in lab_results:
            metric_name = result.metric.name
            if metric_name not in results_by_metric:
                results_by_metric[metric_name] = {
                    'metric': result.metric.to_dict(),
                    'values': []
                }
            
            results_by_metric[metric_name]['values'].append({
                'value': result.value,
                'unit': result.metric.unit,
                'status': result.status,
                'timestamp': result.timestamp.isoformat(),
                'reference_range': result.metric.reference_range,
                'notes': result.notes,
                'source': result.source
            })
        
        return {
            'total_results': lab_results.count(),
            'results_by_metric': results_by_metric,
            'period_days': days
        }
    
    @staticmethod
    def create_custom_metric(user: User, name: str, type: str, unit: str, description: str = "", 
                           min_value: Optional[float] = None, max_value: Optional[float] = None,
                           reference_range: str = "", icon: str = "", color: str = "") -> Metric:
        """Create a custom metric for a user"""
        return Metric.objects.create(
            name=name,
            type=type,
            unit=unit,
            description=description,
            is_custom=True,
            created_by=user,
            is_public=False,  # Custom metrics are private by default
            min_value=min_value,
            max_value=max_value,
            reference_range=reference_range,
            icon=icon,
            color=color
        )
    
    @staticmethod
    def add_metric_value(
        user: User,
        metric_name: str,
        value: float,
        measurement_type: str = 'log',
        notes: str = '',
        source: str = ''
    ) -> MetricValue:
        """Add a new metric value for a user"""
        metric = Metric.objects.get(name=metric_name, is_active=True)
        
        metric_value = MetricValue.objects.create(
            user=user,
            metric=metric,
            value=value,
            measurement_type=measurement_type,
            notes=notes,
            source=source,
            timestamp=timezone.now()
        )
        
        return metric_value

    @staticmethod
    def add_or_update_target(
        user: User,
        metric_name: str,
        target_value: float,
        notes: str = ''
    ) -> MetricValue:
        """Add or update a target value, creating new record if target is older than 1 day"""
        metric = Metric.objects.get(name=metric_name, is_active=True)
        
        # Check if there's an existing target
        existing_target = MetricValue.objects.filter(
            user=user,
            metric=metric,
            measurement_type='target'
        ).order_by('-timestamp').first()
        
        # If no existing target or target is older than 1 day, create new
        if not existing_target or (timezone.now() - existing_target.timestamp).days > 1:
            metric_value = MetricValue.objects.create(
                user=user,
                metric=metric,
                value=target_value,
                measurement_type='target',
                notes=notes,
                source='',
                timestamp=timezone.now()
            )
        else:
            # Update existing target
            existing_target.value = target_value
            existing_target.notes = notes
            existing_target.timestamp = timezone.now()
            existing_target.save()
            metric_value = existing_target
        
        return metric_value
    
    @staticmethod
    def get_available_metrics(user: User, include_custom: bool = True) -> List[Dict[str, Any]]:
        """Get all available metrics for a user"""
        metrics = Metric.objects.filter(is_active=True)
        
        # Include public metrics and user's custom metrics
        if include_custom:
            metrics = metrics.filter(
                models.Q(is_public=True) | 
                models.Q(is_custom=True, created_by=user)
            )
        else:
            metrics = metrics.filter(is_public=True)
        
        return [metric.to_dict() for metric in metrics.order_by('type', 'name')]

    @staticmethod
    def get_user_favorites(user: User) -> List[Dict[str, Any]]:
        """Get user's favorite metrics"""
        favorites = UserMetricFavorite.objects.filter(user=user).select_related('metric').order_by('-created_at')
        return [favorite.metric.to_dict() for favorite in favorites]
    
    @staticmethod
    def get_default_favorites() -> List[str]:
        """Get list of default favorite metric names"""
        return [
            'Weight',
            'Height', 
            'BMI',
            'Body Fat Percentage',
            'Waist Circumference',
            'Total Cholesterol'
        ]
    
    @staticmethod
    def setup_default_favorites(user: User) -> None:
        """Set up default favorites for a new user"""
        default_names = HealthMetricsService.get_default_favorites()
        default_metrics = Metric.objects.filter(name__in=default_names, is_active=True)
        
        for metric in default_metrics:
            UserMetricFavorite.objects.get_or_create(user=user, metric=metric)
    
    @staticmethod
    def toggle_favorite(user: User, metric_id: int) -> Dict[str, Any]:
        """Toggle favorite status for a metric"""
        try:
            metric = Metric.objects.get(id=metric_id, is_active=True)
            favorite, created = UserMetricFavorite.objects.get_or_create(
                user=user, 
                metric=metric
            )
            
            if not created:
                # If it already existed, remove it (toggle off)
                favorite.delete()
                return {
                    'success': True,
                    'is_favorite': False,
                    'message': f'{metric.name} removed from favorites'
                }
            else:
                return {
                    'success': True,
                    'is_favorite': True,
                    'message': f'{metric.name} added to favorites'
                }
                
        except Metric.DoesNotExist:
            return {
                'success': False,
                'error': 'Metric not found'
            }

    @staticmethod
    def evaluate_formula(user: User, formula: str) -> Optional[float]:
        """Evaluate a calculation formula using the latest metric values"""
        try:
            # Get all active metrics to find their IDs
            metrics = Metric.objects.filter(is_active=True)
            metric_values = {}
            
            # Get the latest value for each metric
            for metric in metrics:
                if metric.metric_id:
                    latest_value = MetricValue.objects.filter(
                        user=user,
                        metric=metric,
                        measurement_type__in=['log', 'current', 'baseline']
                    ).order_by('-timestamp').first()
                    
                    if latest_value:
                        metric_values[metric.metric_id] = float(latest_value.value)
            
            # Add age and gender from user profile
            try:
                from user_auth.models import UserProfile
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.date_of_birth:
                    from datetime import date
                    today = date.today()
                    age = today.year - user_profile.date_of_birth.year - ((today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day))
                    metric_values['AGE'] = age
                
                # Add gender for BMR calculation
                if user_profile.gender:
                    metric_values['GENDER'] = user_profile.gender
            except:
                pass
            
            # Replace metric IDs with their values in the formula
            evaluated_formula = formula
            for metric_id, value in metric_values.items():
                evaluated_formula = evaluated_formula.replace(metric_id, str(value))
            
            # Handle special characters and convert to Python syntax
            evaluated_formula = evaluated_formula.replace('²', '**2')  # Convert ² to **2
            evaluated_formula = evaluated_formula.replace('³', '**3')  # Convert ³ to **3
            
            # Evaluate the formula safely
            # Allow basic math operations, power operations, and string comparisons
            allowed_chars = set('0123456789+-*/(). **"\'=<>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
            if not all(c in allowed_chars for c in evaluated_formula):
                return None
            
            result = eval(evaluated_formula)
            if result is not None:
                # Round to 1 decimal place for calculated metrics
                return round(float(result), 1)
            return None
            
        except Exception as e:
            print(f"Formula evaluation error: {e} for formula: {formula}")
            return None

    @staticmethod
    def get_calculated_value(user: User, metric: Metric) -> Optional[float]:
        """Get the calculated value for a metric using its formula"""
        if not metric.is_calculated or not metric.calculation_formula:
            return None
        
        return HealthMetricsService.evaluate_formula(user, metric.calculation_formula)


class HealthCalculatorService:
    """Service for health calculations"""
    
    @staticmethod
    def calculate_lbm(weight_kg: float, body_fat_percentage: float) -> Optional[float]:
        """
        Calculate Lean Body Mass (LBM)
        Formula: LBM = Weight * (1 - Body Fat % / 100)
        """
        if body_fat_percentage > 0:
            return weight_kg * (1 - body_fat_percentage / 100)
        return None
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age_years: int, gender: str) -> float:
        """
        Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
        Formula: 
        - Men: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) + 5
        - Women: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(years) - 161
        """
        if gender == 'male':
            return 10 * weight_kg + 6.25 * height_cm - 5 * age_years + 5
        else:  # female
            return 10 * weight_kg + 6.25 * height_cm - 5 * age_years - 161
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure (TDEE)
        TDEE = BMR × Activity Multiplier
        """
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9,
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        return bmr * multiplier
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """
        Calculate Body Mass Index (BMI)
        Formula: BMI = weight(kg) / height(m)²
        """
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        """Get BMI category based on BMI value"""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    @staticmethod
    def calculate_body_fat_mass(weight_kg: float, body_fat_percentage: float) -> float:
        """
        Calculate body fat mass
        Formula: Body Fat Mass = Weight × (Body Fat % / 100)
        """
        return weight_kg * (body_fat_percentage / 100)
