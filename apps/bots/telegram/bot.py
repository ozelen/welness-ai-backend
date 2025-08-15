from telegrinder import Telegrinder, API, Token
import os
import asyncio
import threading
from telegrinder.modules import logger

logger.set_level("INFO")

api = API(Token(os.getenv("BOT_TOKEN")))
bot = Telegrinder(api)

# Add one more import
from telegrinder import Message

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(bot.run_forever())
    loop.run_forever()

@bot.on.message()
async def message_handler(message: Message):
    if message.text:
        await message.answer(message.text.unwrap())

def init_bot(bot_name):
    logger.info(f"Initializing bot: {bot_name}")
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

# bot.run_forever()
