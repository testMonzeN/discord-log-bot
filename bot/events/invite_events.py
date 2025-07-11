"""
Обработчик событий приглашений
"""

import discord
from .base_event_handler import BaseEventHandler


class InviteEventHandler(BaseEventHandler):
    """Класс для обработки событий приглашений и участников"""
    
    def __init__(self, config_manager, invites_cache=None):
        super().__init__(config_manager)
        self.invites_cache = invites_cache or {}
    
    async def on_invite_create(self, invite: discord.Invite):
        """Обработка создания приглашения"""
        if not self.is_feature_enabled('invite_events'):
            return
            
        log_channel = self.get_log_channel(invite.guild, "invite_events")
        
        embed = self.create_embed(
            title="🎫 Создано новое приглашение!",
            description=f"**Код приглашения:** {invite.code}\n"
                       f"**Создатель:** {invite.inviter.mention}\n"
                       f"**Срок действия:** {f'{invite.max_age} секунд' if invite.max_age else 'Бессрочно'}\n"
                       f"**Максимальное использование:** {invite.max_uses if invite.max_uses else 'Неограничено'}",
            color=discord.Color.blue()
        )
        
        await log_channel.send(embed=embed)
        
        try:
            self.invites_cache[invite.guild.id] = await invite.guild.invites()
        except discord.Forbidden:
            pass
    
    async def on_member_join(self, member: discord.Member):
        """Обработка входа участника"""
        if not self.is_feature_enabled('invite_events'):
            return
            
        log_channel = self.get_log_channel(member.guild, "invite_events")
        
        used_invite = None
        try:
            new_invites = await member.guild.invites()
            
            for invite in self.invites_cache.get(member.guild.id, []):
                for new_invite in new_invites:
                    if invite.code == new_invite.code and invite.uses < new_invite.uses:
                        used_invite = new_invite
                        break
                if used_invite:
                    break
            
            self.invites_cache[member.guild.id] = new_invites
        except discord.Forbidden:
            pass
        
        embed = self.create_embed(
            title="🎉 Новый участник!",
            description=f"Добро пожаловать на сервер, {member.mention}!",
            color=discord.Color.green()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(
            name="Аккаунт создан",
            value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=False
        )
        embed.add_field(
            name="Участников на сервере",
            value=member.guild.member_count,
            inline=False
        )
        
        if used_invite:
            embed.add_field(
                name="Использованное приглашение",
                value=f"**Код:** {used_invite.code}\n"
                      f"**Создатель:** {used_invite.inviter.mention}\n"
                      f"**Использований:** {used_invite.uses}",
                inline=False
            )
        
        await log_channel.send(embed=embed)
    
    async def on_member_remove(self, member: discord.Member):
        """Обработка выхода участника"""
        if not self.is_feature_enabled('invite_events'):
            return
            
        log_channel = self.get_log_channel(member.guild, "invite_events")
        
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "Нет ролей"
        
        embed = self.create_embed(
            title="🚪 Участник покинул сервер",
            description=f"{member.mention} покинул нас. Мы будем скучать!",
            color=discord.Color.red()
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(
            name="Участников на сервере", 
            value=member.guild.member_count, 
            inline=True
        )
        embed.add_field(
            name="Роли", 
            value=roles_str, 
            inline=False
        )
        
        await log_channel.send(embed=embed) 