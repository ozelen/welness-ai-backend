# apps/focusmaite/tgbot/handlers/chat.py
from telegrinder import Dispatch, Message
from telegrinder import logger
from telegrinder.node import FileId, Me, Photo, Video, UserId, as_node
import traceback # For detailed error logging
import json
import asyncio
from typing import Dict, Set
from telegrinder.rules import (
    CallbackDataEq,
    FuzzyText,
    HasText,
    IsUpdateType,
    Markup,
    Text,
)
from ...core.bot import chat_manager
from ..api_instance import api  # Import the API instance from api_instance.py
from ...core.agents import chat_response

# Global state for tracking typing tasks
typing_tasks: Dict[int, asyncio.Task] = {}

dp = Dispatch()

@dp.message()
async def handle_photo(photo_id: FileId[Photo]) -> str:
    return f"Photo ID: {photo_id}"

@dp.message()
async def handle_video(video_id: FileId[Video]) -> str:
    return f"Video ID: {video_id}"

@dp.message(FuzzyText("hello"))
async def hello(message: Message):
    await message.reply("Hi!")
    
@dp.message(Text("/clear"))
async def clear_chat(message: Message):
    """Clear the conversation history for the user."""
    user_id = message.from_user.id
    chat_manager.clear_conversation(user_id)
    await message.reply("Conversation history has been cleared!")

@dp.message(final=False)
async def handle_all_chat_messages(message: Message): # Renamed for clarity
    user_text = message.text.unwrap()
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    for response_chunk in chat_response(user_id, user_text, chat_id):
        await message.answer(response_chunk)
    
    # for response_chunk in chat_manager.get_chat_response(user_id, user_text, chat_id):
    #     await message.answer(response_chunk)
