import json
import os
import sys
import logging
import requests
from datetime import datetime, date
from collections import defaultdict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY", "").strip()
YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID", "").strip()
ADMIN_IDS = [int(id.strip()) for id in os.environ["ADMIN_IDS"].split(",") if id.strip()]

print(f"✅ Токен бота получен")
logger.info(f"Admin IDs: {ADMIN_IDS}")

# Состояния для диалога
WAITING_FOR_LANGUAGE = 1
WAITING_FOR_TEXT = 2

# Хранение состояний пользователей
user_states = defaultdict(dict)


USERS_FILE_PATH = "/tmp/users.json"

def load_users():
    """Загрузка списка пользователей из JSON"""
    if not os.path.exists(USERS_FILE_PATH):
        with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f: 
            json.dump({}, f, ensure_ascii=False)
        users = {}
        for admin_id in ADMIN_IDS:
            users[str(admin_id)] = {
                "username": "",
                "name": "Admin",
                "added": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        save_users(users)
        return users
    
    with open(USERS_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    """Сохранение списка пользователей в JSON"""
    with open(USERS_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


class SimpleTranslator:
    """Переводчик"""
    
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.folder_id = YANDEX_FOLDER_ID
        
        if not self.api_key or not self.folder_id:
            print("API_KEY и FOLDER_ID отсутствуют")
            raise ValueError("API_KEY и FOLDER_ID отсутствуют")
        
        self.max_uses_per_user = 20 
        self.user_usage = {}
        self.current_date = date.today()
        
        print("Переводчик готов к работе")

    def _get_user_key(self, user_id, current_date):
        return f"{user_id}_{current_date}"
    
    def can_user_translate(self, user_id):
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
        if not text or not text.strip():
            return text

        if user_id:
            can_translate, error = self.can_user_translate(user_id)
            if not can_translate:
                return None
        
        if len(text) > 1000:
            return None
        
        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }
        
        data = {
            "folderId": self.folder_id,
            "texts": [text],
            "targetLanguageCode": target_lang
        }
        
        try:
            print(f"Перевод: '{text[:30]}...' на {target_lang}")
            
            response = requests.post(url, json=data, headers=headers, timeout=10)

            if user_id:
                today = date.today()
                user_key = self._get_user_key(user_id, today)
                self.user_usage[user_key] = self.user_usage.get(user_key, 0) + 1
            
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
                return None
                
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
        
    def get_user_usage(self, user_id):
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
        today = date.today()
        user_key = self._get_user_key(user_id, today)
        
        if user_key in self.user_usage:
            self.user_usage[user_key] = 0
            print(f"Сбросил счетчик для пользователя {user_id}")
            return True
        return False
    
    def get_languages(self):
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

translator = SimpleTranslator()


def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_user_allowed(user_id):
    users = load_users()
    return str(user_id) in users

def add_user(user_id, username="", name=""):
    users = load_users()
    
    if str(user_id) in users:
        return False
    
    users[str(user_id)] = {
        "username": username,
        "name": name,
        "added": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    save_users(users)
    return True

def remove_user(user_id):
    users = load_users()
    
    if str(user_id) not in users:
        return False 
    
    del users[str(user_id)]
    save_users(users)
    return True

def get_all_users():
    return load_users()


def send_telegram_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    if not BOT_TOKEN:
        return None
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram API error: {e}")
        return None

def send_typing_action(chat_id):
    if not BOT_TOKEN:
        return None
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction"
    payload = {
        "chat_id": chat_id,
        "action": "typing"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        print(f"Telegram API error (typing): {e}")
        return None

def edit_message(chat_id, message_id, text, parse_mode="HTML", reply_markup=None):
    if not BOT_TOKEN:
        return None
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram API error (edit): {e}")
        return None

def answer_callback_query(callback_query_id, text=""):
    if not BOT_TOKEN:
        return None
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id
    }
    
    if text:
        payload["text"] = text
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        print(f"Telegram API error (callback): {e}")
        return None


def handle_start(chat_id, user_id, user_name=""):
    if not is_user_allowed(user_id):
        return f"Недостаточно прав для использования бота.\n\nВаш ID: {user_id}\nИмя: {user_name}\n\nПерешлите этот ID администратору @apoffeozz для получения доступа."
    
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
    
    print(f"Пользователь {user_name} запустил бота")
    return welcome_text

def handle_help(chat_id, user_id):
    if not is_user_allowed(user_id):
        return "У вас недостаточно прав"
    
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
    
    return help_text

def handle_translate_command(chat_id, user_id, user_name=""):
    if not is_user_allowed(user_id):
        return "У вас недостаточно прав"
    
    print(f"Пользователь {user_name} начал перевод")
    
    can_translate, error = translator.can_user_translate(user_id)
    if not can_translate:
        return f"Превышен дневной лимит: {error}\nИспользуйте /status для проверки."
    

    user_states[user_id]["state"] = WAITING_FOR_LANGUAGE
    
    languages = translator.get_languages()
    
 
    keyboard = []
    popular_languages = ["ru", "en", "es", "fr", "de", "it"]
    
    for lang_code in popular_languages:
        if lang_code in languages:
            lang_name = languages[lang_code]
            keyboard.append([{
                "text": lang_name,
                "callback_data": f"lang_{lang_code}"
            }])
    
    keyboard.append([{"text": "Отмена", "callback_data": "cancel"}])
    
    reply_markup = {
        "inline_keyboard": keyboard
    }
    
 
    send_telegram_message(
        chat_id, 
        "Выберите язык для перевода:",
        reply_markup=json.dumps(reply_markup)
    )
    
    return None 

def handle_language_selection(chat_id, user_id, lang_code, message_id=None):
    if not is_user_allowed(user_id):
        answer_callback_query(chat_id, "У вас недостаточно прав")
        return None
    
    languages = translator.get_languages()
    lang_name = languages.get(lang_code, lang_code)
    
    print(f"Выбран язык: {lang_code} ({lang_name})")
    
    user_states[user_id]["target_lang"] = lang_code
    user_states[user_id]["lang_name"] = lang_name
    user_states[user_id]["state"] = WAITING_FOR_TEXT
    
    answer_callback_query(chat_id, f"Выбран язык: {lang_name}")
    
    if message_id:
        edit_message(
            chat_id, 
            message_id,
            f"Выбран язык: {lang_name}\n\nТеперь введите текст для перевода:"
        )
    else:
        send_telegram_message(
            chat_id,
            f"Выбран язык: {lang_name}\n\nТеперь введите текст для перевода:"
        )
    
    return None

def handle_text_translation(chat_id, user_id, text):
    if not is_user_allowed(user_id):
        return "У вас недостаточно прав"
    
    state = user_states.get(user_id, {}).get("state")
    
    if state == WAITING_FOR_TEXT:
        target_lang = user_states[user_id].get("target_lang", "ru")
        lang_name = user_states[user_id].get("lang_name", "Русский")
        
        print(f"Перевод текста: '{text[:50]}...' на {target_lang}")
        
        # Типо печатает
        send_typing_action(chat_id)
        
        can_translate, error = translator.can_user_translate(user_id)
        if not can_translate:
            # Сброс состояния
            user_states[user_id] = {}
            return f"Превышен дневной лимит: {error}"
        
        translated = translator.translate(text, target_lang=target_lang, user_id=user_id)
        
        user_states[user_id] = {}
        
        if translated:
            response = (
                f"Перевод на {lang_name}:\n\n"
                f"{translated}\n\n"
                f"Для нового перевода: /translate"
            )
            return response
        else:
            return "Не удалось перевести текст.\nПопробуйте еще раз: /translate"
    else:
        # игнор
        return None

def handle_quick_translate(chat_id, user_id, text):
    if not is_user_allowed(user_id):
        return None
    
    if text.startswith('/'):
        return None
    
    print(f"Быстрый перевод: '{text[:50]}...'")
    
    send_typing_action(chat_id)
    
    can_translate, error = translator.can_user_translate(user_id)
    if not can_translate:
        return f"Превышен дневной лимит: {error}"
    
    translated = translator.translate(text, target_lang="ru", user_id=user_id)
    
    if translated:
        keyboard = [
            [{
                "text": "На английский", 
                "callback_data": "quick_en"
            }, {
                "text": "На испанский", 
                "callback_data": "quick_es"
            }]
        ]
        
        reply_markup = {
            "inline_keyboard": keyboard
        }
        
        response = (
            f"Перевод на русский:\n\n"
            f"{translated}\n\n"
            f"Исходный текст:\n"
            f"{text}"
        )
        
        send_telegram_message(
            chat_id, 
            response,
            reply_markup=json.dumps(reply_markup)
        )
        
        return None 
    else:
        return "Не удалось перевести текст. Попробуйте команду /translate"

def handle_quick_button(chat_id, user_id, callback_data, message_id=None):
    answer_callback_query(callback_data, "Для перевода на другие языки используйте команду /translate")
    
    if message_id:
        edit_message(
            chat_id, 
            message_id,
            "Для перевода на другие языки используйте команду /translate"
        )
    
    return None

def handle_languages_command(chat_id, user_id):
    if not is_user_allowed(user_id):
        return "У вас недостаточно прав"
    
    languages = translator.get_languages()
    
    languages_text = "Поддерживаемые языки:\n\n"
    
    for code, name in languages.items():
        languages_text += f"{name} ({code})\n"
    
    return languages_text

def handle_status_command(chat_id, user_id):
    if not is_user_allowed(user_id):
        return "У вас недостаточно прав"
    
    usage = translator.get_user_usage(user_id)
    
    status_text = (
        f"Ваш статус использования:\n\n"
        f"Использовано переводов сегодня: {usage['used']} из {usage['limit']}\n"
        f"Осталось переводов: {usage['remaining']}\n\n"
        f"Лимит: {usage['limit']} переводов в день\n"
        f"Максимальная длина текста: 1000 символов"
    )
    
    return status_text

def handle_cancel(chat_id, user_id):
    if not is_user_allowed(user_id):
        return "У вас недостаточно прав"
    
    # Сброс состояния
    if user_id in user_states:
        user_states[user_id] = {}
    
    return "Перевод отменен."

def handle_adduser_command(user_id, args):
    if not is_admin(user_id):
        return "Только для админа"
    
    if not args:
        return "Напиши: /adduser 123456789"
    
    new_id = args[0]
    
    users = load_users()
    users[new_id] = {
        "username": "",
        "name": "Added by admin",
        "added": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    save_users(users)
    return f"Добавил пользователя {new_id}"

def handle_removeuser_command(user_id, args):
    if not is_admin(user_id):
        return "Только для админа"
    
    if not args:
        return "Напиши: /removeuser id_пользователя"
    
    remove_id = args[0]
    
    users = load_users()

    if is_admin(int(remove_id)):
        return "Извини, но нет"
    
    if remove_id in users:
        del users[remove_id]
        save_users(users)
        return f"Удалил пользователя {remove_id}"
    else:
        return f"Пользователь {remove_id} не найден"

def handle_listusers_command(user_id):
    if not is_admin(user_id):
        return "Только для админа"
    
    users = load_users()
    
    if not users:
        return "Нет пользователей"
    
    text = "Список пользователей:\n\n"
    
    for user_id_val, info in users.items():
        text += f"ID: {user_id_val}\n"
        text += f"Имя: {info.get('name', '---')}\n"
        text += f"Added: {info.get('added', '---')}\n\n"
    
    return text

def handle_unknown_command(chat_id, user_id):
    if not is_user_allowed(user_id):
        return None
    
    return "Неизвестная команда.\nИспользуй /help для просмотра доступных команд"

def handle_callback_query(update):
    query = update.get("callback_query", {})
    if not query:
        return None
    
    callback_query_id = query.get("id")
    data = query.get("data", "")
    user_id = query.get("from", {}).get("id")
    chat_id = query.get("message", {}).get("chat", {}).get("id")
    message_id = query.get("message", {}).get("message_id")
    
    print(f"Callback query: data='{data}', user_id={user_id}")
    
    # Ответ
    answer_callback_query(callback_query_id)
    
    if data == "cancel":
        # Сброс состояния
        if user_id in user_states:
            user_states[user_id] = {}
        
        edit_message(chat_id, message_id, "Перевод отменен")
        return None
    
    elif data.startswith("lang_"):
        lang_code = data.replace("lang_", "")
        handle_language_selection(chat_id, user_id, lang_code, message_id)
        return None
    
    elif data.startswith("quick_"):
        handle_quick_button(chat_id, user_id, callback_query_id, message_id)
        return None
    
    return None

def handler(event, context):
    try:
        logger.info("Handler started")
        
        update = None
        
        if isinstance(event, dict):
            if "body" in event:
                body = event["body"]
                if isinstance(body, str):
                    try:
                        update = json.loads(body)
                    except:
                        update = body
                else:
                    update = body
            elif "update_id" in event or "message" in event or "callback_query" in event:
                update = event
        
        if update is None:
            try:
                if not sys.stdin.isatty():
                    stdin_data = sys.stdin.read()
                    if stdin_data:
                        update = json.loads(stdin_data)
            except:
                pass
        
        if update is None:
            return {"statusCode": 200, "body": json.dumps({"status": "ok"})}
        
        if isinstance(update, str):
            try:
                update = json.loads(update)
            except:
                pass
        
        if "callback_query" in update:
            handle_callback_query(update)
            return {"statusCode": 200, "body": json.dumps({"status": "ok"})}
        
        if not isinstance(update, dict) or "message" not in update:
            return {"statusCode": 200, "body": json.dumps({"status": "ok", "message": "No message"})}
        
        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        user_name = message.get("from", {}).get("first_name", "")
        text = message.get("text", "").strip()
        
        print(f"Processing: user_id={user_id}, text='{text}', state={user_states.get(user_id, {}).get('state')}")
        
        if not chat_id:
            return {"statusCode": 400, "body": json.dumps({"error": "No chat_id"})}
        
        response_text = None
        
        # Проверка состояния
        state = user_states.get(user_id, {}).get("state")
        if state == WAITING_FOR_TEXT and text and not text.startswith('/'):
            response_text = handle_text_translation(chat_id, user_id, text)
            if response_text:
                send_telegram_message(chat_id, response_text)
            return {"statusCode": 200, "body": json.dumps({"status": "ok"})}
        
        if text == "/start":
            response_text = handle_start(chat_id, user_id, user_name)
        
        elif text == "/help":
            response_text = handle_help(chat_id, user_id)
        
        elif text == "/translate":
            handle_translate_command(chat_id, user_id, user_name)
            return {"statusCode": 200, "body": json.dumps({"status": "ok"})}
        
        elif text == "/languages":
            response_text = handle_languages_command(chat_id, user_id)
        
        elif text == "/status":
            response_text = handle_status_command(chat_id, user_id)
        
        elif text == "/cancel":
            response_text = handle_cancel(chat_id, user_id)
            # Сбрасос состояния
            if user_id in user_states:
                user_states[user_id] = {}
        
        elif text.startswith("/adduser"):
            args = text.split()[1:] if len(text.split()) > 1 else []
            response_text = handle_adduser_command(user_id, args)
        
        elif text.startswith("/removeuser"):
            args = text.split()[1:] if len(text.split()) > 1 else []
            response_text = handle_removeuser_command(user_id, args)
        
        elif text == "/listusers":
            response_text = handle_listusers_command(user_id)
        
        elif text.startswith("/"):
            response_text = handle_unknown_command(chat_id, user_id)
        
        else:
            if state != WAITING_FOR_TEXT:
                result = handle_quick_translate(chat_id, user_id, text)
                if result:
                    response_text = result
        
        if response_text is None:
            return {"statusCode": 200, "body": json.dumps({"status": "ok"})}
        
        send_telegram_message(chat_id, response_text)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "ok",
                "chat_id": chat_id,
                "user_id": user_id
            })
        }
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "error", "error": str(e)[:100]})
        }