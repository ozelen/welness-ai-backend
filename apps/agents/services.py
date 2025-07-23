from typing import Dict, Any, List

from .tools import (
    get_user_goals,
    get_user_body_measurements,
    get_user_progress_summary,
    search_goals_by_type,
    get_latest_measurements
)
# from .models import Tool


class AgentService:
    """Service class to handle agent tool execution"""
    
    @staticmethod  # type: ignore
    def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with the given parameters
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Dictionary containing the tool execution result
        """
        # First try to get the tool from database
        try:
            tool = Tool.objects.get(name=tool_name, is_active=True)
            function_name = tool.function_name
        except Tool.DoesNotExist:
            return {'error': f'Tool not found in database: {tool_name}'}
        
        # Map function names to actual functions
        tool_mapping = {
            'get_user_goals': get_user_goals,
            'get_user_body_measurements': get_user_body_measurements,
            'get_user_progress_summary': get_user_progress_summary,
            'search_goals_by_type': search_goals_by_type,
            'get_latest_measurements': get_latest_measurements,
        }
        
        if function_name not in tool_mapping:
            return {'error': f'Unknown function: {function_name}'}
        
        try:
            result = tool_mapping[function_name](**kwargs)
            return {
                'success': True,
                'data': result,
                'tool': tool_name,
                'tool_display_name': tool.display_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name,
                'tool_display_name': tool.display_name
            }
    
    @staticmethod
    def get_user_goals(user_id: int) -> List[Dict[str, Any]]:
        """Get user goals using the tool"""
        return get_user_goals(user_id)
    
    @staticmethod
    def get_user_progress(user_id: int) -> Dict[str, Any]:
        """Get comprehensive user progress"""
        return get_user_progress_summary(user_id)
    
    @staticmethod
    def get_user_measurements(user_id: int, goal_id: str = None) -> List[Dict[str, Any]]:
        """Get user body measurements"""
        return get_user_body_measurements(user_id, goal_id)
    
    @staticmethod
    def search_goals(user_id: int, goal_type: str) -> List[Dict[str, Any]]:
        """Search goals by type"""
        return search_goals_by_type(user_id, goal_type)
    
    @staticmethod
    def get_latest_user_measurements(user_id: int, metric: str = None) -> List[Dict[str, Any]]:
        """Get latest user measurements"""
        return get_latest_measurements(user_id, metric)


class GoalAnalysisService:
    """Service for analyzing user goals and providing insights"""
    
    @staticmethod
    def analyze_goal_progress(user_id: int, goal_id: str) -> Dict[str, Any]:
        """
        Analyze progress for a specific goal
        
        Args:
            user_id: User ID
            goal_id: Goal ID
            
        Returns:
            Analysis results
        """
        # Get goal details
        goals = get_user_goals(user_id)
        goal = next((g for g in goals if g['id'] == goal_id), None)
        
        if not goal:
            return {'error': 'Goal not found'}
        
        # Get measurements for this goal
        measurements = get_user_body_measurements(user_id, goal_id)
        
        # Analyze progress
        analysis = {
            'goal': goal,
            'measurements': measurements,
            'progress_analysis': GoalAnalysisService._analyze_measurements(measurements),
            'recommendations': GoalAnalysisService._generate_recommendations(goal, measurements)
        }
        
        return analysis
    
    @staticmethod
    def _analyze_measurements(measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze measurement data"""
        if not measurements:
            return {'status': 'no_data', 'message': 'No measurements available'}
        
        # Group by metric
        metrics_data = {}
        for measurement in measurements:
            metric = measurement['metric']
            if metric not in metrics_data:
                metrics_data[metric] = []
            metrics_data[metric].append(measurement)
        
        analysis = {}
        for metric, data in metrics_data.items():
            # Sort by timestamp
            sorted_data = sorted(data, key=lambda x: x['timestamp'])
            
            if len(sorted_data) >= 2:
                first = sorted_data[0]
                latest = sorted_data[-1]
                
                change = latest['value'] - first['value']
                change_percent = (change / first['value']) * 100 if first['value'] != 0 else 0
                
                analysis[metric] = {
                    'baseline': first['value'],
                    'current': latest['value'],
                    'change': change,
                    'change_percent': change_percent,
                    'trend': 'improving' if change > 0 else 'declining' if change < 0 else 'stable'
                }
            else:
                analysis[metric] = {
                    'current': data[0]['value'],
                    'status': 'single_measurement'
                }
        
        return analysis
    
    @staticmethod
    def _generate_recommendations(goal: Dict[str, Any], measurements: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on goal and measurements"""
        recommendations = []
        
        goal_type = goal['goal_type']
        
        if goal_type == 'weight_loss':
            recommendations.extend([
                "Focus on creating a caloric deficit through diet and exercise",
                "Track your food intake to ensure you're eating fewer calories than you burn",
                "Include both cardio and strength training in your routine",
                "Aim for 1-2 pounds of weight loss per week for sustainable results"
            ])
        elif goal_type == 'muscle_gain':
            recommendations.extend([
                "Prioritize progressive overload in your strength training",
                "Ensure adequate protein intake (1.6-2.2g per kg of body weight)",
                "Get sufficient rest between workouts for muscle recovery",
                "Focus on compound movements like squats, deadlifts, and bench press"
            ])
        elif goal_type == 'endurance':
            recommendations.extend([
                "Gradually increase your cardio duration and intensity",
                "Include both steady-state and interval training",
                "Focus on proper breathing techniques during exercise",
                "Allow adequate recovery time between intense sessions"
            ])
        
        # Add general recommendations
        recommendations.extend([
            "Stay consistent with your routine",
            "Track your progress regularly",
            "Get adequate sleep (7-9 hours per night)",
            "Stay hydrated throughout the day"
        ])
        
        return recommendations 