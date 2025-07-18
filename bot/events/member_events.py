"""Обработчик событий участников"""

import discord
from datetime import datetime, timedelta
from .base_event_handler import BaseEventHandler
from bot.analytics.analytics_manager import analytics_manager


class MemberEventHandler(BaseEventHandler):
    """
    Обработчик событий участников с интеграцией аналитики.
    """
    """Класс для обработки событий участников"""
    
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Обработка изменений участника"""
        # Тайм-ауты (мьюты)
        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until:
                analytics_manager.data['mutes']['timeout'] += 1
            else:
                analytics_manager.data['mutes']['untimeout'] += 1
            analytics_manager.save()
        await self._handle_timeout_events(before, after)
        await self._handle_role_events(before, after)
    
    async def _handle_timeout_events(self, before: discord.Member, after: discord.Member):
        """Обработка событий мутов"""
        if not self.is_feature_enabled('timeout_events'):
            return
            
        log_channel = self.get_log_channel(after.guild, 'timeout_events')
        
        if not before.is_timed_out() and after.is_timed_out():
            timeout_duration = after.timed_out_until - datetime.utcnow()
            timeout_duration = timeout_duration - timedelta(microseconds=timeout_duration.microseconds)
            moderator = await self.get_moderator_from_audit_log(after.guild, discord.AuditLogAction.member_update)
            
            embed = self.create_embed(
                title="🔇 Пользователь получил мут!",
                description=f"{after.mention} был замучен на {timeout_duration}.\n**Администратор:** {moderator}",
                color=discord.Color.orange()
            )
            await log_channel.send(embed=embed)
        
        elif before.is_timed_out() and not after.is_timed_out():
            embed = self.create_embed(
                title="🔊 Мут снят!",
                description=f"{after.mention} больше не замучен.",
                color=discord.Color.green()
            )
            await log_channel.send(embed=embed)
    
    async def _handle_role_events(self, before: discord.Member, after: discord.Member):
        """Обработка событий ролей"""
        if not self.is_feature_enabled('role_management'):
            return
            
        log_channel = self.get_log_channel(after.guild, 'role_management')
        
        if len(before.roles) < len(after.roles):
            new_role = next(role for role in after.roles if role not in before.roles)
            moderator = await self.get_moderator_from_audit_log(after.guild, discord.AuditLogAction.member_role_update)
            
            embed = self.create_embed(
                title="🎖️ Пользователь получил роль!",
                description=f"{after.mention} получил роль {new_role.mention}.\n**Администратор:** {moderator}",
                color=discord.Color.blue()
            )
            await log_channel.send(embed=embed)
        
        elif len(before.roles) > len(after.roles):
            removed_role = next(role for role in before.roles if role not in after.roles)
            moderator = await self.get_moderator_from_audit_log(after.guild, discord.AuditLogAction.member_role_update)
            
            embed = self.create_embed(
                title="❌ Пользователь потерял роль!",
                description=f"{after.mention} потерял роль {removed_role.mention}.\n**Администратор:** {moderator}",
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed)
    
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Обработка бана участника"""
        if not self.is_feature_enabled('ban_events'):
            return
            
        log_channel = self.get_log_channel(guild, 'ban_events')
        moderator = await self.get_moderator_from_audit_log(guild, discord.AuditLogAction.ban)
        
        embed = self.create_embed(
            title="🔨 Пользователь забанен!",
            description=f"{user.mention} был забанен.\n**Администратор:** {moderator}",
            color=discord.Color.red()
        )
        await log_channel.send(embed=embed)
        analytics_manager.data['bans']['banned'] += 1
        analytics_manager.save()
    
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Обработка разбана участника"""
        if not self.is_feature_enabled('ban_events'):
            return
            
        log_channel = self.get_log_channel(guild, 'ban_events')
        moderator = await self.get_moderator_from_audit_log(guild, discord.AuditLogAction.unban)
        
        embed = self.create_embed(
            title="🎉 Пользователь разбанен!",
            description=f"{user.mention} был разбанен.\n**Администратор:** {moderator}",
            color=discord.Color.green()
        )
        await log_channel.send(embed=embed)
        analytics_manager.data['bans']['unbanned'] += 1
        analytics_manager.save() 

    async def on_member_join(self, member):
        analytics_manager.data['users']['joined'] += 1
        analytics_manager.save()

    async def on_member_remove(self, member):
        analytics_manager.data['users']['left'] += 1
        analytics_manager.save() 