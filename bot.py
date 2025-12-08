"""
bot.py - Главный файл Telegram бота
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Импортирn конфигурациb
from config import BOT_TOKEN

# Импорт обработчиков
from handlers.start_help import start_command, help_command
from handlers.common import unknown_command

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """
    Основная функция запуска
    """
    print("🚀 Запуск бота-переводчика...")
    
    try:
        # Объект управления ботом
        application = Application.builder().token(BOT_TOKEN).build()
        
        print("✅ Application создан")
        
        # Команда /start
        application.add_handler(CommandHandler("start", start_command))
        print("✅ Обработчик /start зарегистрирован")
        
        # Команда /help
        application.add_handler(CommandHandler("help", help_command))
        print("✅ Обработчик /help зарегистрирован")
        
        # Обработчик неизвестных команд
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        print("✅ Обработчик неизвестных команд зарегистрирован")
        
        print("🤖 Бот запущен! Нажми Ctrl+C для остановки")
        print("👉 Перейди в Telegram и найди своего бота")
        print("👉 Отправь ему /start")
        
        # Проверка наличия новых сообщений, когда бот активен
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True 
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        print(f"❌ Критическая ошибка: {e}")
        print("🔧 Проверь:")
        print("   1. Токен бота в .env файле")
        print("   2. Интернет-соединение")
        print("   3. Установлены ли все зависимости: pip install -r requirements.txt")

if __name__ == '__main__':
    # Запуск только при прямом выполнении файла
    main()