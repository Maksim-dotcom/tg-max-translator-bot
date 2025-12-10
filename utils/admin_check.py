"""
admin_check.py - Проверка админов

"""
from config import ADMIN_IDS

def is_admin(user_id):
    """Проверяет, является ли пользователь админом"""
    return user_id in ADMIN_IDS