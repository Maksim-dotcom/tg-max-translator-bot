"""
handlers/translate_handler.py - Простой обработчик перевода
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from services.yandex_translate import translator

# Состояния для диалога
WAITING_FOR_LANGUAGE = 1
WAITING_FOR_TEXT = 2

async def start_translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /translate"""
    
    user = update.effective_user
    user_id = user.id

    print(f"Пользователь {user.first_name} начал перевод")

    # Проверка лимита пользователя
    can_translate, error = translator.can_user_translate(user_id)
    if not can_translate:
        await update.message.reply_text(
            f"Превышен дневной лимит: {error}\n"
            f"Используйте /status для проверки."
        )
        return ConversationHandler.END
    
    # Список языков
    languages = translator.get_languages()
    
    # Создание кнопок
    keyboard = []
    
    # Часто используемые языки
    popular_languages = ["ru", "en", "es", "fr", "de", "it"]
    
    for lang_code in popular_languages:
        if lang_code in languages:
            lang_name = languages[lang_code]
            button = InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
            keyboard.append([button])
    
    # Кнопка отмены
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Выберите язык для перевода:",
        reply_markup=reply_markup
    )
    
    return WAITING_FOR_LANGUAGE


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбор языка"""
    query = update.callback_query
    await query.answer()
    
    # Отмена
    if query.data == "cancel":
        await query.edit_message_text("Перевод отменен")
        return ConversationHandler.END
    
    # Получение кода языка
    if query.data.startswith("lang_"):
        lang_code = query.data.split("_")[1]
        languages = translator.get_languages()
        lang_name = languages.get(lang_code, lang_code)
        
        # Сохранение в контекст
        context.user_data["target_lang"] = lang_code
        context.user_data["lang_name"] = lang_name
        
        print(f"Выбран язык: {lang_code} ({lang_name})")
        
        await query.edit_message_text(
            f"Выбран язык: {lang_name}\n\n"
            f"Теперь введите текст для перевода:"
        )
        
        return WAITING_FOR_TEXT


async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка введенного текста"""
    user_text = update.message.text
    target_lang = context.user_data.get("target_lang", "ru")
    lang_name = context.user_data.get("lang_name", "Русский")
    user_id = update.effective_user.id
    
    print(f"Перевод текста: '{user_text[:50]}...' на {target_lang}")
    
    # Типо печатает
    await update.message.chat.send_action(action="typing")

    #Передача user_id при вызове translate
    translated = translator.translate(user_text, target_lang=target_lang, user_id=user_id)
    
    if translated:
        response = (
            f"Перевод на {lang_name}:\n\n"
            f"{translated}\n\n"
            f"Для нового перевода: /translate"
        )
    else:
        response = (
            "Не удалось перевести текст.\n"
            "Попробуйте еще раз: /translate"
        )
    
    await update.message.reply_text(response)
    
    # Завершаение состояния
    return ConversationHandler.END


async def cancel_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена перевода"""
    await update.message.reply_text("Перевод отменен.")
    return ConversationHandler.END


async def quick_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перевод на русский без определения языка"""
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Пропуск команд
    if user_text.startswith('/'):
        return
    
    print(f"Быстрый перевод: '{user_text[:50]}...'")
    
    await update.message.chat.send_action(action="typing")

    #Передача user_id при вызове translate
    translated = translator.translate(user_text, target_lang="ru", user_id=user_id)
    
    # Перевод на русский
    translated = translator.translate(user_text, target_lang="ru")
    
    if translated:
        # Создание кнопок
        keyboard = [
            [
                InlineKeyboardButton("На английский", callback_data=f"quick_en"),
                InlineKeyboardButton("На испанский", callback_data=f"quick_es")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = (
            f"Перевод на русский:\n\n"
            f"{translated}\n\n"
            f"Исходный текст:\n"
            f"{user_text}"
        )
        
        await update.message.reply_text(response, reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            "Не удалось перевести текст. Попробуйте команду /translate"
        )


async def handle_quick_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Для перевода на другие языки используйте команду /translate"
    )


async def show_languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список языков"""
    languages = translator.get_languages()
    
    languages_text = "Поддерживаемые языки:\n\n"
    
    for code, name in languages.items():
        languages_text += f"{name} ({code})\n"
    
    await update.message.reply_text(languages_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус лимита для пользователя"""
    user_id = update.effective_user.id
    
    # Получение информации об использовании
    usage = translator.get_user_usage(user_id)
    
    status_text = (
        f"Ваш статус использования:\n\n"
        f"Использовано переводов сегодня: {usage['used']} из {usage['limit']}\n"
        f"Осталось переводов: {usage['remaining']}\n\n"
        f"Лимит: {usage['limit']} переводов в день\n"
        f"Максимальная длина текста: 1000 символов"
    )
    
    await update.message.reply_text(status_text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс счетчика для тестов"""
    user_id = update.effective_user.id
    
    # Сброс счетчика
    success = translator.reset_user(user_id)
    
    if success:
        await update.message.reply_text(
            "Ваш счетчик переводов сброшен.\n"
            "Теперь можно снова использовать переводы."
        )
    else:
        await update.message.reply_text(
            "У вас еще не было переводов сегодня.\n"
            "Счетчик уже на нуле."
        )