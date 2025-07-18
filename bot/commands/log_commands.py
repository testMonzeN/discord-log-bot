"""
Команды для управления логами
"""

import discord
from discord.ext import commands
from ..config import ConfigManager
from ..ui import LogButtons
from ..utils.helpers import add_timestamp


class LogCommands(commands.Cog):
    """Класс команд для управления логами"""
    
    def __init__(self, bot: commands.Bot, config_manager: ConfigManager):
        self.bot = bot
        self.config = config_manager
    
    @commands.command(name="setlog-old")
    @commands.has_permissions(administrator=True)
    async def set_log_channel_old(self, ctx, *args):
        """Старая команда настройки каналов логов"""
        await ctx.message.delete()
        guild_id = ctx.guild.id
        enabled_features = self.config.get_enabled_features()
        
        if not args:
            embed = discord.Embed(
                title="❓ Инструкция по использованию команды !setlog",
                description=(
                    "Используйте команду следующим образом:\n"
                    "`!setlog-old #канал all` — настроить канал для всех функций.\n"
                    "`!setlog-old #канал invite_events` — настроить канал для конкретной функции.\n"
                    "`!setlog-old list` — просмотреть текущие настройки каналов.\n"
                    "`!setlog-old clear` — очистить все настройки каналов.\n"
                    "`!setlog-old #канал clear` — очистить настройки для конкретного канала."
                ),
                color=discord.Color.blue()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed, delete_after=30)
            return

        if args[0].lower() == "list":
            log_channels = self.config.get_guild_log_channels(guild_id)
            if not log_channels:
                embed = discord.Embed(
                    title="📋 Список каналов логов",
                    description="Каналы для логов не настроены.",
                    color=discord.Color.blue()
                )
            else:
                description = ""
                for func, channel_id in log_channels.items():
                    channel = ctx.guild.get_channel(channel_id)
                    if channel:
                        description += f"**{func}:** {channel.mention}\n"
                    else:
                        description += f"**{func}:** Канал не найден (ID: {channel_id})\n"

                embed = discord.Embed(
                    title="📋 Список каналов логов",
                    description=description,
                    color=discord.Color.blue()
                )
            add_timestamp(embed)
            await ctx.send(embed=embed, delete_after=30)
            return

        if args[0].lower() == "clear":
            log_channels = self.config.get_guild_log_channels(guild_id)
            if log_channels:
                self.config.clear_guild_log_channels(guild_id)
                embed = discord.Embed(
                    title="✅ Настройки логов очищены!",
                    description="Все настройки каналов логов были удалены.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ Нет настроек для очистки",
                    description="Настройки каналов логов отсутствуют.",
                    color=discord.Color.blue()
                )
            add_timestamp(embed)
            await ctx.send(embed=embed, delete_after=10)
            return

        try:
            channel = await commands.TextChannelConverter().convert(ctx, args[0])
        except commands.ChannelNotFound:
            embed = discord.Embed(
                title="❌ Ошибка!",
                description=f"Канал `{args[0]}` не найден.",
                color=discord.Color.red()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed, delete_after=10)
            return

        if len(args) > 1 and args[1].lower() == "clear":
            self.config.remove_guild_log_channel(guild_id, channel.id)
            embed = discord.Embed(
                title="✅ Настройки канала очищены!",
                description=f"Все настройки для канала {channel.mention} были удалены.",
                color=discord.Color.green()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed, delete_after=10)
            return

        feature = args[1] if len(args) > 1 else "all"

        if feature != "all" and feature not in enabled_features:
            embed = discord.Embed(
                title="❌ Ошибка!",
                description=f"Функция `{feature}` не найдена.\n"
                            f"Доступные функции: {', '.join(enabled_features.keys())}",
                color=discord.Color.red()
            )
            add_timestamp(embed)
            await ctx.send(embed=embed, delete_after=10)
            return

        if feature == "all":
            self.config.set_all_channels_for_guild(guild_id, channel.id)
            description = f"Теперь все уведомления будут отправляться в {channel.mention}."
        else:
            self.config.set_guild_log_channel(guild_id, feature, channel.id)
            description = f"Теперь уведомления для функции `{feature}` будут отправляться в {channel.mention}."

        embed = discord.Embed(
            title="✅ Канал логов настроен!",
            description=description,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name="setlog-new")
    @commands.has_permissions(administrator=True)
    async def setlog_new(self, ctx):
        """Новая интерактивная команда настройки каналов логов"""
        view = LogButtons(ctx.guild, self.config)
        embed = view.get_main_embed()
        
        embed.set_footer(
            text=f"🔧 Настраивает: {ctx.author.display_name} • Тайм-аут интерфейса: 5 минут",
            icon_url=ctx.author.display_avatar.url
        )
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @commands.command(name="quicklog")
    @commands.has_permissions(administrator=True)
    async def quick_log_setup(self, ctx, channel: discord.TextChannel = None):
        """Быстрая настройка одного канала для всех функций"""
        if channel is None:
            channel = ctx.channel
        
        guild_id = ctx.guild.id
        self.config.set_all_channels_for_guild(guild_id, channel.id)

        embed = discord.Embed(
            title="⚡ Быстрая настройка завершена!",
            description=f"Канал {channel.mention} настроен для всех функций логирования.\n"
                       f"Теперь все уведомления будут приходить сюда!",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await ctx.send(embed=embed) 