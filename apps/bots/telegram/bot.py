from telegrinder import Telegrinder
from .handlers import dps
from .api_instance import api  # Import from the new api_instance.py
import asyncio
from django.core.signals import request_finished
from django.dispatch import receiver
import threading
import logging
import os
import atexit

logger = logging.getLogger(__name__)

# Get bot token from environment - This section is removed as API is initialized in api_instance.py
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# if not BOT_TOKEN:
#    raise ValueError("BOT_TOKEN environment variable is not set")
# api = API(token=Token(BOT_TOKEN)) # This line is removed

bot = Telegrinder(api) # api is now imported

# Store the bot task and thread
bot_task = None
bot_thread = None
is_running = False
bot_lock = threading.Lock()

def run_bot():
    """Run the bot in a separate thread."""
    global bot_task, is_running
    logger.info("Starting bot thread")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        bot_task = loop.create_task(bot.run_forever())
        is_running = True
        logger.info("Bot task created and running")
        loop.run_forever()
    except Exception as e:
        logger.error(f"Error in bot thread: {e}")
        is_running = False
    finally:
        loop.close()
        is_running = False
        logger.info("Bot thread stopped")

def init_bot():
    """Initialize the bot and start it in a separate thread."""
    global bot_thread, is_running
    
    with bot_lock:
        if is_running:
            logger.warning("Bot is already running, skipping initialization")
            return
        
        logger.info("Initializing bot...")
        
        # Register all handlers
        for dp in dps:
            logger.info(f"Loading handler {dp}")
            bot.dispatch.load(dp)
        
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot started in background thread")

def stop_bot():
    """Stop the bot gracefully."""
    global bot_task, bot_thread, is_running
    
    with bot_lock:
        if not is_running:
            logger.info("Bot is not running, nothing to stop")
            return
        
        logger.info("Stopping bot...")
        
        if bot_task:
            bot_task.cancel()
            bot_task = None
        
        if bot_thread and bot_thread.is_alive():
            bot_thread.join(timeout=5)
            bot_thread = None
        
        is_running = False
        logger.info("Bot stopped")

# Register cleanup on exit
atexit.register(stop_bot)

@receiver(request_finished)
def handle_request_finished(sender, **kwargs):
    """Handle Django request finished signal."""
    pass  # This is just to keep the signal handler registered
