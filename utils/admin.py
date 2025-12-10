"""
admin.py - Админка
"""

import json
from telegram import Update
from telegram.ext import ContextTypes
from .admin_check import is_admin
from datetime import datetime

def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/adduser id_пользователя"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Только для админа")
        return
    
    if not context.args:
        await update.message.reply_text("Напиши: /adduser 123456789")
        return
    
    new_id = context.args[0]
    
    users = load_users()
    users[new_id] = {
        "username": "",
        "name": "Added by admin",
        "added": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    save_users(users)
    await update.message.reply_text(f"Добавил пользователя {new_id}")

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/removeuser id_пользователя"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Только для админа")
        return
    
    if not context.args:
        await update.message.reply_text("Напиши: /removeuser id_пользователя")
        return
    
    remove_id = context.args[0]
    
    users = load_users()

    if(is_admin(int(remove_id))):
        await update.message.reply_text("Извини, но нет")
        return
    
    if remove_id in users:
        del users[remove_id]
        save_users(users)
        await update.message.reply_text(f"Удалил пользователя {remove_id}")
    else:
        await update.message.reply_text(f"Пользователь {remove_id} не найден")

async def listusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/listusers"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Только для админа")
        return
    
    users = load_users()
    
    if not users:
        await update.message.reply_text("Нет пользователей")
        return
    
    text = "Список пользователей:\n\n"
    
    for user_id, info in users.items():
        text += f"ID: {user_id}\n"
        text += f"Имя: {info.get('name', '---')}\n"
        text += f"Added: {info.get('added', '---')}\n\n"
    
    await update.message.reply_text(text)