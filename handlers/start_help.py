"""
handlers/start_help.py - Обработчики команд /start и /help
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.user_check import is_user_allowed

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start при запуске бота пользователем
    """
    # Получение пользователя
    user = update.effective_user

    # Проверка доступа
    if not is_user_allowed(user.id):
        await update.message.reply_text(
            f"Недостаточно прав для использования бота.\n\n"
            f"Ваш ID: {user.id}\n"
            f"Имя: {user.first_name}\n\n"
            f"Перешлите этот ID администратору @apoffeozz для получения доступа."
        )
        return
    
    # Сообщение
    welcome_text = f"""
    Привет!
    
    Я — бот-переводчик Максимус
    
    Я умею:
    • Переводить текст на разные языки
    • Определять язык исходного текста
    • Сохранять настройки перевода
    
    Команды:
    /start - Запустить бота
    /help - Помощь и инструкции
    /translate - Начать перевод
    /status - Статус использования
    
    Просто отправь текст, чтобы получить перевод! (Доступно 20 в день)
    """
    
    # Отправляем сообщение пользователю
    await update.message.reply_text(welcome_text)
    print(f"Пользователь {user.first_name} запустил бота")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка"""
    
    """Только для пользователей с доступом"""
    user_id = update.effective_user.id
    
    if not is_user_allowed(user_id):
        await update.message.reply_text("У вас недостаточно прав")
        return
    
    help_text = """
        Команды бота:

        /start - Начать работу с ботом
        /help - Показать эту справку
        /translate - Начать перевод текста
        /languages - Показать список языков
        /cancel - Отменить текущий перевод
        /status - Узнать лимит переводов (доступно 20 в день)

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
