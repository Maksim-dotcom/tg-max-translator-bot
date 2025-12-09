## Описание проекта

Telegram-бот для перевода текста с использованием Yandex Translate API. Бот предоставляет функциональность для перевода текста на различные языки с ограничением количества переводов для каждого пользователя. t.me/MaxTranslator_bot (Выполнена имитация деплоя на уже не бесплатный хостинг Railway см. Ветку deploy) 

## Основные возможности

| Команда | Описание |
|---------|----------|
| `/start` | Запустить бота и получить приветственное сообщение |
| `/help` | Показать справку и инструкции |
| `/translate` | Начать процесс перевода с выбором языка |
| `/languages` | Показать список поддерживаемых языков |
| `/status` | Узнать лимит переводов |
| `/cancel` | Отменить текущий перевод |

### Лимиты использования

- Каждый пользователь: 20 переводов в день
- Максимальная длина текста: 1000 символов

## Структура проекта
tg-max-translator-bot/
├── .gitignore
├── bot.py
├── config.py
├── Procfile
├── requirements.txt
├── runtime.txt
├── railway.json
├── services/
│ └── yandex_translate.py
├── handlers/
│ ├── start_help.py
│ ├── common.py
│ └── translate_handler.py
└── utils/


## Технологии

- Python 3.11+
- python-telegram-bot 22.5
- Yandex Translate API
- Requests для HTTP-запросов
- python-dotenv для управления переменными окружения

## Установка и запуск

### 1. Предварительные требования

- Python 3.11 или выше
- Аккаунт в Yandex Cloud с активированным сервисом Translate
- Telegram Bot Token от @BotFather

### 2. Настройка переменных окружения

Создать файл `.env` в корневой директории проекта:

BOT_TOKEN=ваш_токен_бота

Yandex Translate API
YANDEX_API_KEY=ваш_api_ключ
YANDEX_FOLDER_ID=ваш_folder_id

### 3. Установка зависимостей
pip install -r requirements.txt

### Ключевые особенности

- Использование ConversationHandler для многошаговых сценариев
- Ограничение использования через систему лимитов
- Обработка ошибок и исключительных ситуаций
- Поддержка polling и webhook режимов

### Демонстрация работы

![Демо GIF](./assets/animation.gif)