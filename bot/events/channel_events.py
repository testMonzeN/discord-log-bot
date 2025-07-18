"""Обработчик событий каналов"""

import discord
from .base_event_handler import BaseEventHandler
from bot.analytics.analytics_manager import analytics_manager


class ChannelEventHandler(BaseEventHandler):
    """
    Обработчик событий каналов с интеграцией аналитики.
    """
    
    async def on_guild_channel_create(self, channel):
        """Обработка создания канала"""
        if not self.is_feature_enabled('channel_events'):
            return
            
        channel_type = "📝 текстовый" if isinstance(channel, discord.TextChannel) else "🎤 голосовой"
        log_channel = self.get_log_channel(channel.guild, 'channel_events')
        
        embed = self.create_embed(
            title="🎉 Создан новый канал!",
            description=f"**Тип канала:** {channel_type}\n**Название:** {channel.mention}",
            color=discord.Color.green()
        )
        await log_channel.send(embed=embed)
        analytics_manager.data['channels']['created'] += 1
        analytics_manager.save()
    
    async def on_guild_channel_delete(self, channel):
        """Обработка удаления канала"""
        if not self.is_feature_enabled('channel_events'):
            return
            
        channel_type = "📝 текстовый" if isinstance(channel, discord.TextChannel) else "🎤 голосовой"
        log_channel = self.get_log_channel(channel.guild, 'channel_events')
        
        embed = self.create_embed(
            title="🗑️ Канал удален!",
            description=f"**Тип канала:** {channel_type}\n**Название:** {channel.name}",
            color=discord.Color.red()
        )
        await log_channel.send(embed=embed)
        analytics_manager.data['channels']['deleted'] += 1
        analytics_manager.save() 