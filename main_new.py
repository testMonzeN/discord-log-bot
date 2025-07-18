"""
Discord Log Bot v2.0.0 - Модульная версия

Система логирования событий Discord сервера с модульной архитектурой.
"""

import discord
import os
from discord.ext import commands

from bot.config import ConfigManager
from bot.events import (
    InviteEventHandler, VoiceEventHandler, MessageEventHandler,
    MemberEventHandler, ChannelEventHandler, RoleEventHandler
)
from bot.commands import LogCommands, ToggleCommands, UtilityCommands, StatsCommands


class KaradevLogBot(commands.Bot):
    """Главный класс бота"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        self.config = ConfigManager()
        self.invites_cache = {}
        
        self.invite_handler = InviteEventHandler(self.config, self.invites_cache)
        self.voice_handler = VoiceEventHandler(self.config)
        self.message_handler = MessageEventHandler(self.config)
        self.member_handler = MemberEventHandler(self.config)
        self.channel_handler = ChannelEventHandler(self.config)
        self.role_handler = RoleEventHandler(self.config)
        
        print("🤖 KaradevLogBot v2.0.0 инициализирован")
    
    async def setup_hook(self):
        """Настройка бота после запуска"""
        await self.add_cog(LogCommands(self, self.config))
        await self.add_cog(ToggleCommands(self, self.config))
        await self.add_cog(UtilityCommands(self, self.config))
        await self.add_cog(StatsCommands(self))
        print("📦 Все модули загружены")
    
    async def on_ready(self):
        """Событие готовности бота"""
        print(f'🚀 Бот {self.user.name} успешно запущен!')
        guild_count = self.config.get_total_guild_count()
        print(f'📊 Настройки загружены: {guild_count} серверов сохранены')
        
        await self.change_presence(
            activity=discord.Game(name="с твоим отцом в прятки")
        )

        for guild in self.guilds:
            try:
                self.invites_cache[guild.id] = await guild.invites()
            except discord.Forbidden:
                print(f"⚠️ Нет прав на просмотр приглашений на сервере {guild.name}")
            
            log_channels = self.config.get_guild_log_channels(guild.id)
            if log_channels:
                print(f"📋 Сервер '{guild.name}': настроено {len(log_channels)} каналов логов")
    
    async def on_invite_create(self, invite):
        await self.invite_handler.on_invite_create(invite)
    
    async def on_member_join(self, member):
        await self.invite_handler.on_member_join(member)
    
    async def on_member_remove(self, member):
        await self.invite_handler.on_member_remove(member)
    
    async def on_voice_state_update(self, member, before, after):
        await self.voice_handler.on_voice_state_update(member, before, after)
    
    async def on_message_delete(self, message):
        await self.message_handler.on_message_delete(message)
    
    async def on_message_edit(self, before, after):
        await self.message_handler.on_message_edit(before, after)
    
    async def on_member_update(self, before, after):
        await self.member_handler.on_member_update(before, after)
    
    async def on_member_ban(self, guild, user):
        await self.member_handler.on_member_ban(guild, user)
    
    async def on_member_unban(self, guild, user):
        await self.member_handler.on_member_unban(guild, user)
    
    async def on_guild_channel_create(self, channel):
        await self.channel_handler.on_guild_channel_create(channel)
    
    async def on_guild_channel_delete(self, channel):
        await self.channel_handler.on_guild_channel_delete(channel)
    
    async def on_guild_role_create(self, role):
        await self.role_handler.on_guild_role_create(role)
    
    async def on_guild_role_delete(self, role):
        await self.role_handler.on_guild_role_delete(role)


def main():
    """Главная функция запуска бота"""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        token = 'YOUR_TOKEN'
        print("⚠️ Используется токен по умолчанию. Для безопасности используйте переменную DISCORD_TOKEN")
    
    bot = KaradevLogBot()
    
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")


if __name__ == "__main__":
    main() 