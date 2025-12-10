"""
user_check.py - Проверка прав пользователя
"""

import json
import os
from datetime import datetime
from config import ADMIN_IDS

def load_users():
    """Загрузка списка пользователей из JSON"""
    if not os.path.exists('users.json'):
        # Создание файла с админом из .env
        with open('users.json', 'w', encoding='utf-8') as f: 
            json.dump({}, f, ensure_ascii=False)
        users = load_users()
        for admin_id in ADMIN_IDS:
            users[str(admin_id)] = {
                "username": "",
                "name": "Admin",
                "added": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        
        save_users(users)
        return {}
    
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    """Сохранение списка пользователей в JSON"""
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def is_user_allowed(user_id):
    """Проверка на наличие в списке"""
    users = load_users()
    return str(user_id) in users

def add_user(user_id, username="", name=""):
    """Добавление пользователя"""
    users = load_users()
    
    if str(user_id) in users:
        return False  # Уже есть
    
    users[str(user_id)] = {
        "username": username,
        "name": name,
        "added": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    save_users(users)
    return True

def remove_user(user_id):
    """Удаление пользователя"""
    users = load_users()
    
    if str(user_id) not in users:
        return False 
    
    del users[str(user_id)]
    save_users(users)
    return True

def get_all_users():
    """Получение всех пользователей"""
    return load_users()