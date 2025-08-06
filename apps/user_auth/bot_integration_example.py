"""
Example integration of user_auth module with existing telegrinder bot

This file shows how to use the TelegramAuthService in your existing bot handlers
to identify users and manage connections.
"""

from telegrinder import Dispatch, Message
from telegrinder.rules import Text
from telegrinder.tools.formatting import HTMLFormatter
from .telegram_auth import (
    TelegramAuthService, 
    get_django_user_from_telegram,
    is_telegram_user_connected,
    get_telegram_connection_code
)

# Example bot handlers that integrate with user_auth

dp = Dispatch()


@dp.message(Text("/start"))
async def start(message: Message):
    """Enhanced start command with user identification"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Check if user is already connected
    if is_telegram_user_connected(user_id):
        django_user = get_django_user_from_telegram(user_id)
        welcome_text = (
            f"Welcome back, {django_user.first_name or django_user.username}!\n\n"
            "You're already connected to your Wellness AI account.\n"
            "Use /profile to see your account details."
        )
    else:
        # Generate connection code for new users
        connection_code = get_telegram_connection_code(user_id)
        welcome_text = (
            f"Hello {message.from_user.first_name}!\n\n"
            "Welcome to Wellness AI Bot! 🤖\n\n"
            "To get started, connect your Telegram account to your Wellness AI account:\n\n"
            f"🔗 Connection Code: `{connection_code}`\n\n"
            "1. Go to your Wellness AI dashboard\n"
            "2. Navigate to Settings > Integrations > Telegram\n"
            "3. Enter this code to connect your account\n\n"
            "Or use /connect to get connection instructions."
        )
    
    await message.reply(
        HTMLFormatter(welcome_text),
        parse_mode=HTMLFormatter.PARSE_MODE,
    )


@dp.message(Text("/connect"))
async def connect(message: Message):
    """Handle user connection request"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    if is_telegram_user_connected(user_id):
        django_user = get_django_user_from_telegram(user_id)
        response_text = (
            f"✅ You're already connected as {django_user.email}\n\n"
            "Use /disconnect to unlink your account if needed."
        )
    else:
        connection_code = get_telegram_connection_code(user_id)
        response_text = (
            "🔗 Connect your Telegram account to Wellness AI\n\n"
            f"Your connection code: `{connection_code}`\n\n"
            "**Steps to connect:**\n"
            "1. Go to your Wellness AI dashboard\n"
            "2. Navigate to Settings > Integrations > Telegram\n"
            "3. Enter the connection code above\n"
            "4. Click 'Connect Account'\n\n"
            "Once connected, you'll receive notifications and updates here!"
        )
    
    await message.reply(
        HTMLFormatter(response_text),
        parse_mode=HTMLFormatter.PARSE_MODE,
    )


@dp.message(Text("/profile"))
async def profile(message: Message):
    """Show user profile information"""
    user_id = message.from_user.id
    
    if not is_telegram_user_connected(user_id):
        await message.reply(
            HTMLFormatter(
                "❌ You're not connected to a Wellness AI account.\n"
                "Use /connect to link your account first."
            ),
            parse_mode=HTMLFormatter.PARSE_MODE,
        )
        return
    
    django_user = get_django_user_from_telegram(user_id)
    integration = TelegramAuthService.get_telegram_integration(django_user)
    
    profile_text = (
        f"👤 **Your Profile**\n\n"
        f"**Name:** {django_user.get_full_name() or 'Not set'}\n"
        f"**Email:** {django_user.email}\n"
        f"**Username:** @{django_user.username}\n"
        f"**Joined:** {django_user.date_joined.strftime('%B %d, %Y')}\n\n"
        f"**Telegram:** @{message.from_user.username or 'No username'}\n"
        f"**Notifications:** {'✅ Enabled' if integration.notifications_enabled else '❌ Disabled'}\n\n"
        "Use /help to see available commands."
    )
    
    await message.reply(
        HTMLFormatter(profile_text),
        parse_mode=HTMLFormatter.PARSE_MODE,
    )


@dp.message(Text("/disconnect"))
async def disconnect(message: Message):
    """Handle user disconnection request"""
    user_id = message.from_user.id
    
    if not is_telegram_user_connected(user_id):
        await message.reply(
            HTMLFormatter("❌ You're not connected to any Wellness AI account."),
            parse_mode=HTMLFormatter.PARSE_MODE,
        )
        return
    
    django_user = get_django_user_from_telegram(user_id)
    success = TelegramAuthService.disconnect_user(django_user)
    
    if success:
        await message.reply(
            HTMLFormatter("✅ Your Telegram account has been disconnected from Wellness AI."),
            parse_mode=HTMLFormatter.PARSE_MODE,
        )
    else:
        await message.reply(
            HTMLFormatter("❌ Failed to disconnect your account. Please try again."),
            parse_mode=HTMLFormatter.PARSE_MODE,
        )


@dp.message(Text("/help"))
async def help_command(message: Message):
    """Show help information"""
    help_text = (
        "🤖 **Wellness AI Bot Commands**\n\n"
        "**Account Management:**\n"
        "• `/start` - Welcome message and connection status\n"
        "• `/connect` - Connect your Telegram account\n"
        "• `/disconnect` - Unlink your Telegram account\n"
        "• `/profile` - View your profile information\n"
        "• `/help` - Show this help message\n\n"
        "**Features:**\n"
        "• 📅 Calendar events and reminders\n"
        "• 📝 Document creation and management\n"
        "• 🎯 Goal tracking and progress\n"
        "• 📊 Health insights and analytics\n\n"
        "**Support:**\n"
        "For technical support, contact us at support@wellness-ai.com"
    )
    
    await message.reply(
        HTMLFormatter(help_text),
        parse_mode=HTMLFormatter.PARSE_MODE,
    )


# Example of how to send notifications to connected users
async def send_notification_to_user(django_user, message_text: str):
    """Example function to send notifications to connected users"""
    from user_auth.telegram_auth import TelegramAuthService
    
    integration = TelegramAuthService.get_telegram_integration(django_user)
    if integration and integration.notifications_enabled:
        # You would use your bot's API to send the message
        # This is just an example - you'd integrate with your existing bot setup
        pass


# Example of how to check user authentication in other handlers
@dp.message(Text("/calendar"))
async def calendar_command(message: Message):
    """Example of a command that requires authentication"""
    user_id = message.from_user.id
    
    if not is_telegram_user_connected(user_id):
        await message.reply(
            HTMLFormatter(
                "❌ You need to connect your account first.\n"
                "Use /connect to link your Telegram account to Wellness AI."
            ),
            parse_mode=HTMLFormatter.PARSE_MODE,
        )
        return
    
    # User is authenticated, proceed with calendar functionality
    django_user = get_django_user_from_telegram(user_id)
    
    # Here you would implement calendar functionality
    # For example, show upcoming events, create new events, etc.
    
    await message.reply(
        HTMLFormatter("📅 Calendar functionality coming soon!"),
        parse_mode=HTMLFormatter.PARSE_MODE,
    ) 