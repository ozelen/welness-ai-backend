from langgraph.prebuilt import create_react_agent
from typing import List, Callable

from collections import defaultdict
from typing import Any, Dict, Optional, Generator

class BotAgent:

    def __init__(self, name: str, model: str, tools: List[Callable], prompt: str):
        self.graph = create_react_agent(name=name, model=model, tools=tools, prompt=prompt)

    def get_chat_response(self, user_id: int, message: str, stream: bool) -> Generator[str, None, None]:
        """Get the chat response for the specified user and message."""
        return self.graph.stream(inputs={"messages": [{"role": "user", "content": message}]}, stream_mode="updates")
