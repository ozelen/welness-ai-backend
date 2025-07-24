from django.apps import AppConfig
from django.utils.functional import cached_property
from .telegram.tg_bot_controller import TgBotController

class BotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bots'
    bots = {}
    
    @cached_property
    def get_bots(self):
        """Get all bots from the database and initialize the corresponding bot controller"""
        from .models import Bot
        bots = Bot.objects.all()
        print(f"Found {len(bots)} bots")
        for bot in bots:
            if bot.provider == 'telegram':
                self.bots[bot.name] = TgBotController(bot)
                print(f"Initializing Bot: {bot.name}")
            else:
                print(f"{bot.provider} is not supported")

    def ready(self):
        """Initialize the bots"""
        return self.get_bots
