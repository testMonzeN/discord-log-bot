"""Обработчик событий ролей"""

import discord
from .base_event_handler import BaseEventHandler
from bot.analytics.analytics_manager import analytics_manager


class RoleEventHandler(BaseEventHandler):
    """
    Обработчик событий ролей с интеграцией аналитики.
    """
    
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
        analytics_manager.data['roles']['created'] += 1
        analytics_manager.save()
    
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
        analytics_manager.data['roles']['deleted'] += 1
        analytics_manager.save()

    async def on_member_update(self, before, after):
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        for role in added_roles:
            role_id = str(role.id)
            analytics_manager.data['roles']['added'][role_id] = analytics_manager.data['roles']['added'].get(role_id, 0) + 1
        for role in removed_roles:
            role_id = str(role.id)
            analytics_manager.data['roles']['removed'][role_id] = analytics_manager.data['roles']['removed'].get(role_id, 0) + 1
        analytics_manager.save() 