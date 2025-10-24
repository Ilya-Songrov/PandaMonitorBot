"""
Utility decorators for the bot
"""

import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import settings

logger = logging.getLogger(__name__)

def authorized_only(func):
    """Decorator to check if user is authorized to use the bot"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if user_id not in settings.ALLOWED_USER_IDS:
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            await update.message.reply_text(
                "❌ У вас немає доступу до цього бота.\n"
                "Зверніться до адміністратора для отримання доступу."
            )
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def admin_only(func):
    """Decorator for admin-only commands (for future use)"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # For now, treat first user in ALLOWED_USER_IDS as admin
        admin_id = settings.ALLOWED_USER_IDS[0] if settings.ALLOWED_USER_IDS else None
        
        if user_id != admin_id:
            logger.warning(f"Non-admin user {user_id} tried to access admin command")
            await update.message.reply_text("❌ Тільки адміністратор може використовувати цю команду.")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper