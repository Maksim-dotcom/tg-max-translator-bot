"""
services/yandex_translate.py - работа с API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class SimpleTranslator:
    """Переводчик"""
    
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        
        if not self.api_key or not self.folder_id:
            print("API_KEY и FOLDER_ID отсутствуют в .env")
            raise ValueError("API_KEY и FOLDER_ID отсутствуют в .env")
        
        print("Переводчик готов к работе")
    
    def translate(self, text, target_lang="ru"):
        """
        Осуществление переврода
        text - текст для перевода
        target_lang - язык перевода (например, "ru", "en")
        """
        if not text or not text.strip():
            return text
        
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