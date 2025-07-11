"""
Вспомогательные функции для Discord Log Bot
"""

import discord
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import ConfigManager


def add_timestamp(embed: discord.Embed) -> None:
    """Добавляет временную метку к embed сообщению"""
    embed.set_footer(text=f"Время события: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")


def get_log_channel(guild: discord.Guild, feature: str, config_manager: "ConfigManager") -> discord.TextChannel:
    """
    Получает канал логов для конкретной функции
    
    Args:
        guild: Discord сервер
        feature: Название функции (invite_events, voice_activity, etc.)
        config_manager: Менеджер конфигурации
        
    Returns:
        TextChannel: Канал для логов или канал по умолчанию
    """
    log_channels = config_manager.get_guild_log_channels(guild.id)
    
    if feature in log_channels:
        channel_id = log_channels[feature]
        channel = guild.get_channel(channel_id)
        if channel:
            return channel
    
    default_channel = guild.system_channel or guild.text_channels[0]
    return default_channel


def get_moderator_from_audit_log(guild: discord.Guild, action: discord.AuditLogAction, 
                                target_id: Optional[int] = None) -> str:
    """
    Получает модератора из audit logs
    
    Args:
        guild: Discord сервер
        action: Тип действия в audit log
        target_id: ID цели действия (опционально)
        
    Returns:
        str: Упоминание модератора или "Неизвестный администратор"
    """
    try:
        async def get_moderator():
            async for entry in guild.audit_logs(action=action, limit=1):
                if target_id is None or entry.target.id == target_id:
                    return entry.user.mention
            return "Неизвестный администратор"
        
        return get_moderator()
    except:
        return "Неизвестный администратор"


def format_role_list(roles: list, exclude_everyone: bool = True) -> str:
    """
    Форматирует список ролей для отображения
    
    Args:
        roles: Список ролей
        exclude_everyone: Исключить роль @everyone
        
    Returns:
        str: Отформатированный список ролей
    """
    if exclude_everyone:
        roles = [role for role in roles if role.name != "@everyone"]
    
    if not roles:
        return "Нет ролей"
    
    role_mentions = [role.mention for role in roles]
    return ", ".join(role_mentions)


def get_feature_emoji(feature: str) -> str:
    """
    Получает эмодзи для функции
    
    Args:
        feature: Название функции
        
    Returns:
        str: Эмодзи
    """
    emojis = {
        "invite_events": "🎫",
        "voice_activity": "🎧", 
        "message_events": "💬",
        "role_events": "🎨",
        "channel_events": "📁",
        "ban_events": "🔨",
        "timeout_events": "🔇",
        "role_management": "🎖️"
    }
    return emojis.get(feature, "📝")


def get_feature_name(feature: str) -> str:
    """
    Получает читаемое название функции
    
    Args:
        feature: Название функции
        
    Returns:
        str: Читаемое название
    """
    names = {
        "invite_events": "События приглашений",
        "voice_activity": "Голосовая активность", 
        "message_events": "События сообщений",
        "role_events": "События ролей",
        "channel_events": "События каналов",
        "ban_events": "События банов",
        "timeout_events": "События мутов",
        "role_management": "Управление ролями"
    }
    return names.get(feature, feature) 