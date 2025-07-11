"""
Базовый класс для обработчиков событий Discord Log Bot
"""

import discord
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import ConfigManager
from ..utils.helpers import add_timestamp, get_log_channel


class BaseEventHandler(ABC):
    """Базовый класс для всех обработчиков событий"""
    
    def __init__(self, config_manager: "ConfigManager"):
        self.config = config_manager
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Проверяет, включена ли функция"""
        enabled_features = self.config.get_enabled_features()
        return enabled_features.get(feature, False)
    
    def get_log_channel(self, guild: discord.Guild, feature: str) -> discord.TextChannel:
        """Получает канал логов для функции"""
        return get_log_channel(guild, feature, self.config)
    
    def create_embed(self, title: str, description: str, color: discord.Color) -> discord.Embed:
        """Создает embed с временной меткой"""
        embed = discord.Embed(title=title, description=description, color=color)
        add_timestamp(embed)
        return embed
    
    async def get_moderator_from_audit_log(self, guild: discord.Guild, 
                                         action: discord.AuditLogAction) -> str:
        """Получает модератора из audit logs"""
        try:
            async for entry in guild.audit_logs(action=action, limit=1):
                return entry.user.mention
        except:
            pass
        return "Неизвестный администратор" 