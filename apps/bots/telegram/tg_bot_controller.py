# bots/bot_controller.py
from ..base_bot_controller import BaseBotController
from telegrinder import Telegrinder, API, Token
import threading
import logging
import atexit
import asyncio
from .handlers import dps

logger = logging.getLogger(__name__)

class TgBotController(BaseBotController):
    def __init__(self, bot_model):
        self.bot_task = None
        self.bot_model = bot_model
        self.client = Telegrinder(API(token=Token(bot_model.api_key)))
        self.thread = None
        self.bot_lock = threading.Lock()
        self.is_running = False
        atexit.register(self.stop)
        logger.info(f"BotController initialized for {bot_model.name}")

    def start(self):
        """Initialize the bot and start it in a separate thread."""
        
        with self.bot_lock:
            if self.is_running:
                logger.warning("Bot is already running, skipping initialization")
                return
            
            logger.info("Initializing bot...")
            
            # Register all telegram handlers
            for dp in dps:
                logger.info(f"Loading handler {dp}")
                self.client.dispatch.load(dp)
            
            # Start bot in a separate thread
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            logger.info("Bot started in background thread")

    def stop(self):
        """Stop the bot gracefully."""
        
        with self.bot_lock:
            if not self.is_running:
                logger.info("Bot is not running, nothing to stop")
                return
            
            logger.info("Stopping bot...")
            
            if self.bot_task:
                self.bot_task.cancel()
                self.bot_task = None
            
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
                self.thread = None
            
            self.is_running =  False
            logger.info("Bot stopped")

    def run(self):
        """Run the bot in a separate thread."""
        logger.info("Starting bot thread")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            self.bot_task = loop.create_task(self.client.run_forever())
            logger.info("Bot task created and running")
            loop.run_forever()
        except Exception as e:
            logger.error(f"Error in bot thread: {e}")   
            self.is_running = False
        finally:
            loop.close()
            self.is_running = False
            logger.info("Bot thread stopped")
    
    def __str__(self):
        return f"BotController for {self.bot_model.name}"