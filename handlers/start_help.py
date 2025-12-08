"""
handlers/start_help.py - Обработчики команд /start и /help
"""

from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start при запуске бота пользователем
    """
    # Получение пользователя
    user = update.effective_user
    
    # Сообщение
    welcome_text = f"""
    Привет, {user.first_name}!
    
    Я — бот-переводчик Максимус
    
    Я умею:
    • Переводить текст на разные языки
    • Определять язык исходного текста
    • Сохранять настройки перевода
    
    Команды:
    /start - Запустить бота
    /help - Помощь и инструкции
    /translate - Начать перевод
    
    Просто отправь текст, чтобы получить перевод!
    """
    
    # Отправляем сообщение пользователю
    await update.message.reply_text(welcome_text)
    print(f"✅ Пользователь {user.first_name} запустил бота")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help для справки по использованию
    """
    help_text = """
    Основные команды:
    /start - Запустить бота и увидеть приветствие
    /help - Показать эту справку
    /translate - Начать процесс перевода
    """
    
    await update.message.reply_text(help_text)
    print(f"✅ Пользователь {update.effective_user.first_name} запросил помощь")


# Экспорт функций для использования в других файлах
__all__ = ['start_command', 'help_command']
