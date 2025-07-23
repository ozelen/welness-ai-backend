from django.db import models
from langgraph.prebuilt import create_react_agent
from functools import cached_property

class Agent(models.Model):
    name = models.CharField(max_length=255)
    supervisor = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    prompt = models.TextField()
    model = models.CharField(max_length=255)
    
    # Agent configuration
    config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @cached_property
    def graph(self):
        """Create and cache the LangGraph agent instance"""
        tools = self.get_tools()
        return create_react_agent(
            str(self.model),
            tools=tools,
            prompt=str(self.prompt),
        )
    
    def create_graph(self):
        """Create and return a LangGraph agent instance"""
        tools = self.get_tools()
        return create_react_agent(
            str(self.model),
            tools=tools,
            prompt=str(self.prompt),
        )
    
    def get_tools(self):
        """Get hardcoded tools for this agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_user_goals",
                    "description": "Get all active goals for a specific user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of the user"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_body_measurements",
                    "description": "Get body measurements for a specific user, optionally filtered by goal",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of the user"
                            },
                            "goal_id": {
                                "type": "string",
                                "description": "Optional goal ID to filter measurements"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_progress_summary",
                    "description": "Get a comprehensive summary of user's goals and progress",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of the user"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_goals_by_type",
                    "description": "Search for goals by type for a specific user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of the user"
                            },
                            "goal_type": {
                                "type": "string",
                                "description": "The type of goal to search for (e.g., 'weight_loss', 'muscle_gain')"
                            }
                        },
                        "required": ["user_id", "goal_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_latest_measurements",
                    "description": "Get the latest measurements for a user, optionally filtered by metric",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "The ID of the user"
                            },
                            "metric": {
                                "type": "string",
                                "description": "Optional metric to filter by (e.g., 'weight_kg', 'body_fat_percentage')"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            }
        ]
    
    def run(self, input_data):
        """Run the agent with input data"""
        return self.graph.invoke(input_data)
