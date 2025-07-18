"""Обработчик событий сообщений"""

import discord
from .base_event_handler import BaseEventHandler
from bot.analytics.analytics_manager import analytics_manager


class MessageEventHandler(BaseEventHandler):
    """
    Обработчик событий сообщений с интеграцией аналитики.
    """
    
    async def on_message(self, message):
        analytics_manager.data['messages']['sent'] += 1
        user_id = str(message.author.id)
        top = analytics_manager.data['messages']['top_senders']
        top[user_id] = top.get(user_id, 0) + 1
        analytics_manager.save()
    
    async def on_message_delete(self, message: discord.Message):
        """Обработка удаления сообщения"""
        if not self.is_feature_enabled("message_events") or not message.guild:
            return
            
        log_channel = self.get_log_channel(message.guild, 'message_events')
        
        embed = self.create_embed(
            title="🗑️ Сообщение удалено!",
            description=f"**Автор:** {message.author.mention}\n"
                       f"**Сообщение:** {message.content}\n",
            color=discord.Color.dark_red()
        )
        
        await log_channel.send(embed=embed)
        analytics_manager.data['messages']['deleted'] += 1
        analytics_manager.save()
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Обработка редактирования сообщения"""
        if (not self.is_feature_enabled('message_events') or 
            not before.guild or before.content == after.content):
            return
            
        log_channel = self.get_log_channel(before.guild, 'message_events')
        
        embed = self.create_embed(
            title="✏️ Сообщение отредактировано!",
            description=f"**Автор:** {before.author.mention}\n"
                       f"**Было:** {before.content}\n"
                       f"**Стало:** {after.content}",
            color=discord.Color.gold()
        )
        
        await log_channel.send(embed=embed)
        analytics_manager.data['messages']['edited'] += 1
        analytics_manager.save() 