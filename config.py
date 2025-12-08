"""
config.py - Загрузка конфигурации и переменных окружения
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Получение токена бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Проверь файл .env")

print("✅ Токен бота получен")