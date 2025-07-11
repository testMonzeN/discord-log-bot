"""
Служебные команды
"""

import discord
from discord.ext import commands
from ..config import ConfigManager
from ..utils.helpers import add_timestamp


class UtilityCommands(commands.Cog):
    """Класс служебных команд"""
    
    def __init__(self, bot: commands.Bot, config_manager: ConfigManager):
        self.bot = bot
        self.config = config_manager
    
    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload_settings_command(self, ctx):
        """Команда для ручной перезагрузки настроек из файла"""
        await ctx.message.delete()
        
        settings = self.config.get_settings()
        guild_count = self.config.get_total_guild_count()
        
        embed = discord.Embed(
            title="🔄 Настройки перезагружены!",
            description=f"Настройки успешно перезагружены из файла.\n"
                       f"Загружено серверов: **{guild_count}**",
            color=discord.Color.blue()
        )
        add_timestamp(embed)
        await ctx.send(embed=embed, delete_after=10) 