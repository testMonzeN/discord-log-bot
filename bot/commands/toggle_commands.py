"""
Команды для управления включением/выключением функций
"""

import discord
from discord.ext import commands
from ..config import ConfigManager
from ..utils.helpers import add_timestamp


class ToggleCommands(commands.Cog):
    """Класс команд для управления функциями бота"""
    
    def __init__(self, bot: commands.Bot, config_manager: ConfigManager):
        self.bot = bot
        self.config = config_manager
    
    @commands.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle_feature(self, ctx, feature: str = None):
        """Управление включением/выключением функций"""
        enabled_features = self.config.get_enabled_features()
        
        if feature == "list":
            status_description = "\n".join(
                f"**{feature}:** {'🟢 Включено' if enabled else '🔴 Выключено'}"
                for feature, enabled in enabled_features.items()
            )

            embed = discord.Embed(
                title="📊 Список функций бота",
                description=status_description,
                color=discord.Color.blue()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed)
            return

        if feature == "on":
            self.config.toggle_all_features(True)
            
            embed = discord.Embed(
                title="✅ Все функции включены!",
                description="Все функции бота теперь **включены**.",
                color=discord.Color.green()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed)
            return

        if feature == "off":
            self.config.toggle_all_features(False)
            
            embed = discord.Embed(
                title="🔴 Все функции выключены!",
                description="Все функции бота теперь **выключены**.",
                color=discord.Color.red()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed)
            return

        if feature not in enabled_features:
            embed = discord.Embed(
                title="❌ Ошибка!",
                description=f"Функция `{feature}` не найдена.\n"
                            f"Доступные функции: {', '.join(enabled_features.keys())}",
                color=discord.Color.red()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed)
            return

        new_state = not enabled_features[feature]
        self.config.set_enabled_feature(feature, new_state)
        state = "включена" if new_state else "выключена"

        embed = discord.Embed(
            title="✅ Состояние функции изменено!",
            description=f"Функция `{feature}` теперь **{state}**.",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await ctx.send(embed=embed) 