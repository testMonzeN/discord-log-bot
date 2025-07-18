"""
Менеджер конфигурации для Discord Log Bot

Отвечает за:
- Чтение/запись настроек из JSON файла
- Управление настройками серверов  
- Управление включенными функциями
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Класс для управления настройками бота"""
    
    def __init__(self, settings_file: str = "bot_settings.json"):
        self.settings_file = settings_file
        self.default_features = {
            "invite_events": True,
            "voice_activity": True,
            "message_events": True,
            "role_events": True,
            "channel_events": True,
            "ban_events": True,
            "timeout_events": True,
            "role_management": True,
        }
        self._ensure_settings_file()
    
    def _ensure_settings_file(self) -> Dict[str, Any]:
        """Создает файл настроек если его нет или он поврежден"""
        default_settings = {
            "enabled_features": self.default_features.copy(),
            "guild_settings": {}
        }
        
        if not os.path.exists(self.settings_file):
            print("Создаем новый файл настроек")
            self._save_settings(default_settings)
            return default_settings
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("Файл настроек пустой, создаем новый")
                    self._save_settings(default_settings)
                    return default_settings
                
                data = json.loads(content)
                
                if "enabled_features" not in data:
                    data["enabled_features"] = self.default_features.copy()
                if "guild_settings" not in data:
                    data["guild_settings"] = {}
                
                for feature in self.default_features:
                    if feature not in data["enabled_features"]:
                        data["enabled_features"][feature] = True
                
                self._save_settings(data)
                return data
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"Ошибка загрузки настроек: {e}")
            print("Создаем новый файл настроек")
            self._save_settings(default_settings)
            return default_settings
    
    def get_settings(self) -> Dict[str, Any]:
        """Получает все настройки из JSON файла"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return self._ensure_settings_file()
    
    def _save_settings(self, settings: Dict[str, Any]) -> None:
        """Сохраняет настройки в JSON файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            print(f"Настройки сохранены успешно")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get_enabled_features(self) -> Dict[str, bool]:
        """Получает статус включенных функций"""
        settings = self.get_settings()
        return settings.get("enabled_features", {})
    
    def set_enabled_feature(self, feature: str, enabled: bool) -> None:
        """Устанавливает статус функции"""
        settings = self.get_settings()
        if "enabled_features" not in settings:
            settings["enabled_features"] = {}
        settings["enabled_features"][feature] = enabled
        self._save_settings(settings)
    
    def toggle_all_features(self, enabled: bool) -> None:
        """Включает/выключает все функции"""
        settings = self.get_settings()
        for feature in settings["enabled_features"]:
            settings["enabled_features"][feature] = enabled
        self._save_settings(settings)
    
    def get_guild_log_channels(self, guild_id: int) -> Dict[str, int]:
        """Получает настройки каналов логов для конкретного сервера"""
        settings = self.get_settings()
        guild_id_str = str(guild_id)
        return settings.get("guild_settings", {}).get(guild_id_str, {}).get("log_channels", {})
    
    def set_guild_log_channel(self, guild_id: int, feature: str, channel_id: int) -> None:
        """Устанавливает канал логов для конкретной функции на сервере"""
        settings = self.get_settings()
        guild_id_str = str(guild_id)
        
        if "guild_settings" not in settings:
            settings["guild_settings"] = {}
        if guild_id_str not in settings["guild_settings"]:
            settings["guild_settings"][guild_id_str] = {}
        if "log_channels" not in settings["guild_settings"][guild_id_str]:
            settings["guild_settings"][guild_id_str]["log_channels"] = {}
        
        settings["guild_settings"][guild_id_str]["log_channels"][feature] = channel_id
        self._save_settings(settings)
        print(f"[SAVE] Установлен канал {channel_id} для функции {feature} на сервере {guild_id}")
    
    def clear_guild_log_channels(self, guild_id: int) -> None:
        """Очищает все настройки каналов для сервера"""
        settings = self.get_settings()
        guild_id_str = str(guild_id)
        
        if "guild_settings" in settings and guild_id_str in settings["guild_settings"]:
            if "log_channels" in settings["guild_settings"][guild_id_str]:
                settings["guild_settings"][guild_id_str]["log_channels"] = {}
                self._save_settings(settings)
                print(f"[CLEAR] Очищены все каналы логов для сервера {guild_id}")
    
    def remove_guild_log_channel(self, guild_id: int, channel_id: int) -> None:
        """Удаляет все настройки для конкретного канала"""
        settings = self.get_settings()
        guild_id_str = str(guild_id)
        
        if "guild_settings" in settings and guild_id_str in settings["guild_settings"]:
            if "log_channels" in settings["guild_settings"][guild_id_str]:
                log_channels = settings["guild_settings"][guild_id_str]["log_channels"]
                to_remove = [func for func, ch_id in log_channels.items() if ch_id == channel_id]
                for func in to_remove:
                    del log_channels[func]
                self._save_settings(settings)
                print(f"[REMOVE] Удален канал {channel_id} из настроек сервера {guild_id}")
    
    def set_all_channels_for_guild(self, guild_id: int, channel_id: int) -> None:
        """Устанавливает один канал для всех функций сервера"""
        enabled_features = self.get_enabled_features()
        for feature in enabled_features:
            self.set_guild_log_channel(guild_id, feature, channel_id)
    
    def get_guild_stats(self, guild_id: int) -> Dict[str, int]:
        """Получает статистику настроек для сервера"""
        log_channels = self.get_guild_log_channels(guild_id)
        return {
            "configured_functions": len(log_channels),
            "unique_channels": len(set(log_channels.values())) if log_channels else 0
        }
    
    def get_total_guild_count(self) -> int:
        """Получает общее количество настроенных серверов"""
        settings = self.get_settings()
        return len(settings.get("guild_settings", {})) 