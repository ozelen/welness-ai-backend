from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .services import AgentService
from .tools import get_user_goals, get_user_progress_summary

@csrf_exempt
@require_http_methods(["POST"])
def chat_endpoint(request):
    """Handle chat messages from Flutter app"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        user_id = data.get('user_id', 1)
        
        # Simple response logic - you can enhance this with your LangGraph agents
        if 'goal' in message.lower():
            goals = get_user_goals(user_id)
            response = f"I can help you with your goals! You have {len(goals)} active goals."
        elif 'meal' in message.lower():
            response = "Great! I can help you log your meals and plan your nutrition."
        elif 'workout' in message.lower():
            response = "Excellent! Let's track your workout progress and keep you motivated."
        elif 'hello' in message.lower() or 'hi' in message.lower():
            response = "Hello! I'm WellAI, your wellness assistant. How can I help you today?"
        else:
            response = "I'm here to help with your wellness journey! You can ask me about goals, meals, workouts, or anything wellness-related."
        
        return JsonResponse({
            'response': response,
            'metadata': {
                'user_id': user_id,
                'message_type': 'text'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def chat_history(request, user_id):
    """Get chat history for a user"""
    # TODO: Implement chat history storage and retrieval
    return JsonResponse([])
