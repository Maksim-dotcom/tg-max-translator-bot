"""
services/yandex_translate.py - работа с API
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()

class SimpleTranslator:
    """Переводчик"""
    
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        
        if not self.api_key or not self.folder_id:
            print("API_KEY и FOLDER_ID отсутствуют в .env")
            raise ValueError("API_KEY и FOLDER_ID отсутствуют в .env")
        
        # Лимит на каждого пользователя 20 переводов в день
        self.max_uses_per_user = 20 
        self.user_usage = {}
        self.current_date = date.today()
        
        print("Переводчик готов к работе")

    def _get_user_key(self, user_id, current_date):
        """Запоминание пользователя"""
        return f"{user_id}_{current_date}"
    
    def can_user_translate(self, user_id):
        """Проверка лимита пользователя"""
        # Сброс счетчика лимитов с нового дня
        today = date.today()
        if today != self.current_date:
            self.user_usage = {}
            self.current_date = today
            print("Сбросил счетчики")
        
        user_key = self._get_user_key(user_id, today)
        user_count = self.user_usage.get(user_key, 0)
        
        if user_count >= self.max_uses_per_user:
            return False, f"Вы использовали {user_count} из {self.max_uses_per_user} переводов сегодня"
        
        return True, ""     
    
    def translate(self, text, target_lang="ru", user_id=None):
        """
        Осуществление переврода
        text - текст для перевода
        target_lang - язык перевода (например, "ru", "en")
        """
        if not text or not text.strip():
            return text

        # Проверяка лимита пользователя
        if user_id:
            can_translate, error = self.can_user_translate(user_id)
            if not can_translate:
                return None, error
        
        # Проверка длины текста
        if len(text) > 1000:
            return None, "Текст слишком длинный (максимум 1000 символов)"
        
        # URL для API
        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        
        # Заголовки запроса
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }
        
        # Данные для запроса
        data = {
            "folderId": self.folder_id,
            "texts": [text],
            "targetLanguageCode": target_lang
        }
        
        try:
            print(f"Перевод: '{text[:30]}...' на {target_lang}")
            
            # Отправка запроса
            response = requests.post(url, json=data, headers=headers, timeout=10)

            # Увеличивание счетчика пользователя
            if user_id:
                today = date.today()
                user_key = self._get_user_key(user_id, today)
                self.user_usage[user_key] = self.user_usage.get(user_key, 0) + 1
            
            # Проверка ответа
            if response.status_code == 200:
                result = response.json()
                translations = result.get("translations", [])
                
                if translations:
                    translated_text = translations[0].get("text", "")
                    print("Успешно переведено")
                    return translated_text
                else:
                    print("Ошибка: нет перевода в ответе")
                    return None
            else:
                print(f"Ошибка API: {response.status_code}")
                print(f"Ответ: {response.text[:100]}")
                return None
                
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
        
    def get_user_usage(self, user_id):
        """Информация об использовании для пользователя"""
        today = date.today()
        user_key = self._get_user_key(user_id, today)
        user_count = self.user_usage.get(user_key, 0)
        
        remaining = self.max_uses_per_user - user_count
        
        return {
            "used": user_count,
            "limit": self.max_uses_per_user,
            "remaining": remaining
        }
    
    def reset_user(self, user_id):
        """Тестовый сброс для себя"""
        today = date.today()
        user_key = self._get_user_key(user_id, today)
        
        if user_key in self.user_usage:
            self.user_usage[user_key] = 0
            print(f"Сбросил счетчик для пользователя {user_id}")
            return True
        return False
    
    def get_languages(self):
        """Возвращает словарь поддерживаемых языков"""
        languages = {
            "ru": "Русский",
            "en": "Английский", 
            "es": "Испанский",
            "fr": "Французский",
            "de": "Немецкий",
            "it": "Итальянский",
            "zh": "Китайский",
            "ja": "Японский",
            "ko": "Корейский",
        }
        return languages


# Глобальный экземпляр
translator = SimpleTranslator()