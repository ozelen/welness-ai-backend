from typing import List, Dict, Any, Optional
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from goals.models import Goal, BodyMeasurement
from datetime import datetime, date

def get_user_goals(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all active goals for a specific user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of dictionaries containing goal information
    """
    try:
        user = User.objects.get(id=user_id)
        goals = Goal.objects.filter(user=user, is_active=True)
        
        return [goal.to_dict() for goal in goals]
    except ObjectDoesNotExist:
        return []
    except Exception as e:
        return [{'error': f'Failed to fetch goals: {str(e)}'}]


def get_user_body_measurements(user_id: int, goal_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get body measurements for a specific user, optionally filtered by goal.
    
    Args:
        user_id: The ID of the user
        goal_id: Optional goal ID to filter measurements
        
    Returns:
        List of dictionaries containing measurement information
    """
    try:
        user = User.objects.get(id=user_id)
        measurements = BodyMeasurement.objects.filter(user=user)
        
        if goal_id:
            measurements = measurements.filter(goal_id=goal_id)
        
        return [measurement.to_dict() for measurement in measurements]
    except ObjectDoesNotExist:
        return []
    except Exception as e:
        return [{'error': f'Failed to fetch measurements: {str(e)}'}]


def get_user_progress_summary(user_id: int) -> Dict[str, Any]:
    """
    Get a comprehensive summary of user's goals and progress.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dictionary containing user's goals and progress summary
    """
    try:
        user = User.objects.get(id=user_id)
        goals = Goal.objects.filter(user=user, is_active=True)
        
        summary = {
            'user_id': user_id,
            'username': user.username,
            'total_active_goals': goals.count(),
            'goals': [],
            'progress_summary': {}
        }
        
        for goal in goals:
            goal_data = goal.to_dict()
            goal_data['measurements'] = get_user_body_measurements(user_id, str(goal.id))
            summary['goals'].append(goal_data)
        
        return summary
    except ObjectDoesNotExist:
        return {'error': f'User with ID {user_id} not found'}
    except Exception as e:
        return {'error': f'Failed to fetch progress summary: {str(e)}'}


def search_goals_by_type(user_id: int, goal_type: str) -> List[Dict[str, Any]]:
    """
    Search for goals by type for a specific user.
    
    Args:
        user_id: The ID of the user
        goal_type: The type of goal to search for (e.g., 'weight_loss', 'muscle_gain')
        
    Returns:
        List of dictionaries containing goal information
    """
    try:
        user = User.objects.get(id=user_id)
        goals = Goal.objects.filter(user=user, goal_type=goal_type, is_active=True)
        
        return [goal.to_dict() for goal in goals]
    except ObjectDoesNotExist:
        return []
    except Exception as e:
        return [{'error': f'Failed to search goals: {str(e)}'}]


def get_latest_measurements(user_id: int, metric: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get the latest measurements for a user, optionally filtered by metric.
    
    Args:
        user_id: The ID of the user
        metric: Optional metric to filter by (e.g., 'weight_kg', 'body_fat_percentage')
        
    Returns:
        List of dictionaries containing the latest measurements
    """
    try:
        user = User.objects.get(id=user_id)
        measurements = BodyMeasurement.objects.filter(user=user)
        
        if metric:
            measurements = measurements.filter(metric=metric)
        
        # Get the latest measurement for each metric
        latest_measurements = []
        seen_metrics = set()
        
        for measurement in measurements.order_by('-timestamp'):
            if measurement.metric not in seen_metrics:
                measurement_data = measurement.to_dict()
                latest_measurements.append(measurement_data)
                seen_metrics.add(measurement.metric)
        
        return latest_measurements
    except ObjectDoesNotExist:
        return []
    except Exception as e:
        return [{'error': f'Failed to fetch latest measurements: {str(e)}'}] 