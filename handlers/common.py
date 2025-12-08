"""
handlers/common.py - Общие обработчики
"""

from telegram import Update
from telegram.ext import ContextTypes


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик неизвестных команд
    """
    await update.message.reply_text(
        "Неизвестная команда.\n"
        "Используй /help для просмотра доступных команд"
    )


__all__ = ['unknown_command']