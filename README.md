## Описание проекта

Telegram-бот для перевода текста с использованием Yandex Translate API. Бот предоставляет функциональность для перевода текста на различные языки с ограничением количества переводов для каждого пользователя. [Max-Translator-bot](https://t.me/MaxTranslator_bot). Выполненен деплой на Yandex Cloud Functions, реализована админская часть, чтобы не выйти за рамки гранта.

## Основные возможности

| Команда | Описание |
|---------|----------|
| `/start` | Запустить бота и получить приветственное сообщение |
| `/help` | Показать справку и инструкции |
| `/translate` | Начать процесс перевода с выбором языка |
| `/languages` | Показать список поддерживаемых языков |
| `/status` | Узнать лимит переводов |
| `/cancel` | Отменить текущий перевод |
| `/adduser user_id` | Дать пользователю доступ к использованию бота |
| `/removeuser user_id` | Отнять доступ у пользователя |
| `/listusers` | Просмотр пользователей которым выдан доступ к боту |

### Лимиты использования

- Каждый пользователь: 20 переводов в день
- Максимальная длина текста: 1000 символов

## Технологии

- Python 3.11+
- python-telegram-bot 22.5
- Yandex Translate API
- Yandex Cloud Functions
- Requests для HTTP-запросов
- python-dotenv для управления переменными окружения

## Установка и запуск

### 1. Предварительные требования

- Python 3.11 или выше
- Аккаунт в Yandex Cloud с активированными сервисами Translate и Cloud Functions
- Telegram Bot Token от @BotFather

### 2. Настройка переменных окружения

Создать файл `.env` в корневой директории проекта:

BOT_TOKEN=ваш_токен_бота

Yandex Translate API
YANDEX_API_KEY=ваш_api_ключ
YANDEX_FOLDER_ID=ваш_folder_id
ADMIN_IDS=id_админов_через_запятую_без_пробелов

### 4. Деплой на Yandex Cloud Functions
```
powrshell

#Очищение временной папки
$tempDir = "temp_deploy_exact"
Remove-Item $tempDir -Recurse -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $tempDir | Out-Null

# 2. Копирование файлов
Copy-Item "yc_function.py" "$tempDir/" -Force
Copy-Item "requirements.txt" "$tempDir/" -Force

# 3. Создание архива
Compress-Archive -Path "$tempDir\*" -DestinationPath "deploy_exact.zip" -CompressionLevel Optimal -Force

Write-Host "Архив создан" -ForegroundColor Green

# 4. Деплой
yc serverless function version create `
  --function-name=tg-translator-bot `
  --runtime=python311 `
  --entrypoint=yc_function.handler `
  --memory=256m `
  --execution-timeout=30s `
  --source-path="./deploy_exact.zip" `
  --environment="BOT_TOKEN=$env:BOT_TOKEN" `
  --environment="YANDEX_API_KEY=$env:YANDEX_API_KEY" `
  --environment="YANDEX_FOLDER_ID=$env:YANDEX_FOLDER_ID" `
  --environment="ADMIN_IDS=$env:ADMIN_IDS"
  ```

### Ключевые особенности

- Использование ConversationHandler для многошаговых сценариев
- Ограничение использования через систему лимитов
- Обработка ошибок и исключительных ситуаций
- Роли: администратор, пользователь
- Поддержка polling и webhook режимов