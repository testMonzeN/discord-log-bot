"""Обработчик событий ролей"""

import discord
from .base_event_handler import BaseEventHandler


class RoleEventHandler(BaseEventHandler):
    """Класс для обработки событий ролей"""
    
    async def on_guild_role_create(self, role: discord.Role):
        """Обработка создания роли"""
        if not self.is_feature_enabled('role_events'):
            return
            
        log_channel = self.get_log_channel(role.guild, 'role_events')
        moderator = await self.get_moderator_from_audit_log(role.guild, discord.AuditLogAction.role_create)
        
        embed = self.create_embed(
            title="🎨 Создана новая роль!",
            description=f"**Роль:** {role.mention}\n"
                       f"**Цвет:** {str(role.color)}\n"
                       f"**Администратор:** {moderator}",
            color=discord.Color.green()
        )
        await log_channel.send(embed=embed)
    
    async def on_guild_role_delete(self, role: discord.Role):
        """Обработка удаления роли"""
        if not self.is_feature_enabled('role_events'):
            return
            
        log_channel = self.get_log_channel(role.guild, 'role_events')
        moderator = await self.get_moderator_from_audit_log(role.guild, discord.AuditLogAction.role_delete)
        
        embed = self.create_embed(
            title="🗑️ Роль удалена!",
            description=f"**Роль:** @{role.name}\n"
                       f"**Цвет:** {str(role.color)}\n"
                       f"**Администратор:** {moderator}",
            color=discord.Color.red()
        )
        await log_channel.send(embed=embed) 