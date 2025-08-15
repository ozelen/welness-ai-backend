from django.apps import AppConfig
from .telegram.tg_bot_controller import TgBotController
from telegrinder.modules import logger
logger.set_level("INFO")

class BotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bots'
    bots = {}
    
    # @cached_property
    def init_custom_bots(self):
        """Get all bots from the database and initialize the corresponding bot controller"""
        from .models import Bot
        bots = Bot.objects.all()
        logger.info(f"Found {len(bots)} bots")
        for bot in bots:
            if bot.provider == 'telegram':
                self.bots[bot.name] = TgBotController(bot)
                self.bots[bot.name].start()
                logger.info(f"Initializing Bot: {bot.name}")
            else:
                logger.error(f"{bot.provider} is not supported")

    def init_bot(self, bot_name):
        """Initialize the bot"""
        from .telegram.bot import init_bot
        init_bot(bot_name)
    
    def ready(self):
        """Initialize the bots"""
        self.init_bot("tg-bot")
        
        # return self.init_custom_bots()
