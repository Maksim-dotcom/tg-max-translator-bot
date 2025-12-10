"""
handlers/common.py - Общие обработчики
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.user_check import is_user_allowed


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик неизвестных команд
    """

    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        return

    await update.message.reply_text(
        "Неизвестная команда.\n"
        "Используй /help для просмотра доступных команд"
    )


__all__ = ['unknown_command']