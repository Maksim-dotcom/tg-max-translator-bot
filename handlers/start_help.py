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
    print(f"Пользователь {user.first_name} запустил бота")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    help_text = """
        Команды бота:

        /start - Начать работу с ботом
        /help - Показать эту справку
        /translate - Начать перевод текста
        /languages - Показать список языков
        /cancel - Отменить текущий перевод

        Использование:

        1. Для перевода с выбором языка:
        - Отправьте /translate
        - Выберите язык из списка
        - Введите текст для перевода

        2. Для быстрого перевода на русский:
        - Просто отправьте любой текст
        - Бот автоматически переведет его

        Поддерживаемые языки: русский, английский, испанский, французский, немецкий, итальянский и другие.
    """
    
    await update.message.reply_text(help_text)


# Экспорт функций для использования в других файлах
__all__ = ['start_command', 'help_command']
