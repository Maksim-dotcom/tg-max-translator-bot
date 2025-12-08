"""
bot.py - Главный файл Telegram бота
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler

from config import BOT_TOKEN

# Импорт обработчиков
from handlers.start_help import start_command, help_command
from handlers.common import unknown_command
from handlers.translate_handler import (
    start_translate_command, language_selected, process_text,
    cancel_translate, quick_translate, handle_quick_button,
    show_languages_command,
    WAITING_FOR_LANGUAGE, WAITING_FOR_TEXT
)

# Красивое логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Запуск бота"""
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        print("Application создан")
        
        # Состояние для перевода
        translate_handler = ConversationHandler(
            entry_points=[CommandHandler("translate", start_translate_command)],
            states={
                WAITING_FOR_LANGUAGE: [
                    CallbackQueryHandler(language_selected)
                ],
                WAITING_FOR_TEXT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, process_text)
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_translate)]
        )
        
        # Регистрация обработчиков
        
        # Базовые команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("languages", show_languages_command))
        
        # Перевод
        application.add_handler(translate_handler)
        
        # Быстрый перевод
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quick_translate))
        
        # Кнопки быстрого перевода
        application.add_handler(CallbackQueryHandler(handle_quick_button, pattern="^quick_"))
        
        # Неизвестные команды
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        print("Бот запущен!")
        
        # Запуск бота
        application.run_polling(allowed_updates=["message", "callback_query"])
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()