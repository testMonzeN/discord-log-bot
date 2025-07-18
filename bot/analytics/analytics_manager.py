"""
Модуль аналитики для сбора и предоставления статистики по ролям, пользователям, сообщениям, приглашениям, голосовой активности, каналам, банам и мьютам Discord-сервера.
"""

import json
import os
from typing import Dict, Any
from bot.utils.backup import backup_file

class AnalyticsManager:
    """
    Класс для сбора, хранения и предоставления статистики по всем ключевым событиям Discord-сервера.
    """
    def __init__(self, path: str = 'analytics.json'):
        self.path = path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'roles': {'added': {}, 'removed': {}, 'created': 0, 'deleted': 0},
            'users': {'joined': 0, 'left': 0, 'top_active': {}},
            'messages': {'sent': 0, 'deleted': 0, 'edited': 0, 'top_senders': {}},
            'invites': {'created': 0, 'used': 0},
            'voice': {'join': 0, 'leave': 0, 'mute': 0, 'unmute': 0},
            'channels': {'created': 0, 'deleted': 0},
            'bans': {'banned': 0, 'unbanned': 0},
            'mutes': {'timeout': 0, 'untimeout': 0}
        }

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        backup_file(self.path)

analytics_manager = AnalyticsManager() 