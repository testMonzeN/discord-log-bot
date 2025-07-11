"""
Дополнительные методы для LogButtons класса
"""

import discord
from discord.ui import Button, Select
from ..utils.helpers import add_timestamp, get_feature_emoji, get_feature_name
from .modals import ClearLogsModal


async def set_specific(self, interaction: discord.Interaction):
    """Настройка отдельных функций"""
    self.current_page = "select_function"
    self.clear_items()
    
    enabled_features = self.config.get_enabled_features()
    options = [
        discord.SelectOption(
            label=get_feature_name(func), 
            value=func,
            emoji=get_feature_emoji(func),
            description=f"Настроить логи для {get_feature_name(func).lower()}"
        )
        for func in enabled_features
    ]
    
    func_select = Select(placeholder="🎯 Выберите функцию для настройки...", options=options, max_values=1)
    
    async def func_select_callback(interaction: discord.Interaction):
        feature = func_select.values[0]
        self.current_feature = feature
        self.clear_items()
        
        channel_options = [
            discord.SelectOption(label=f"#{channel.name}", value=str(channel.id), emoji="📁")
            for channel in self.guild.text_channels[:25]
        ]
        
        channel_select = Select(placeholder="📁 Выберите канал...", options=channel_options)
        
        async def channel_select_callback(interaction: discord.Interaction):
            try:
                channel_id = int(channel_select.values[0])
                channel = self.guild.get_channel(channel_id)
                
                if channel:
                    guild_id = self.guild.id
                    print(f"[DEBUG] Индивидуальная настройка {feature} для сервера {guild_id}")
                    
                    self.config.set_guild_log_channel(guild_id, feature, channel_id)
                    
                    emoji = get_feature_emoji(feature)
                    name = get_feature_name(feature)
                    
                    embed = discord.Embed(
                        title="✅ Индивидуальная настройка завершена!",
                        description=f"{emoji} **{name}**\n\n"
                                   f"📍 Канал настроен: {channel.mention}\n"
                                   f"💾 Настройки автоматически сохранены!",
                        color=0x5865f2
                    )
                    embed.add_field(
                        name="💡 Полезно знать:",
                        value="Вы можете настроить разные каналы для разных типов событий!",
                        inline=False
                    )
                    embed.add_field(
                        name="🎉 Готово!",
                        value="Используйте кнопку **◀️ Назад** для возврата в главное меню.",
                        inline=False
                    )
                    add_timestamp(embed)
                    
                    self.clear_items()
                    back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
                    back_btn.callback = lambda i: self.show_main_menu(i)
                    self.add_item(back_btn)
                    
                    await interaction.response.edit_message(embed=embed, view=self)
                else:
                    embed = discord.Embed(
                        title="❌ Ошибка!",
                        description="🚫 **Канал не найден!**\n\n💡 Попробуйте выбрать канал еще раз.",
                        color=0xed4245
                    )
                    add_timestamp(embed)
                    await interaction.response.edit_message(embed=embed, view=self)
            except Exception as e:
                print(f"Ошибка в channel_select_callback: {e}")
                embed = discord.Embed(
                    title="❌ Произошла ошибка!",
                    description="🚫 **Не удалось настроить канал.**\n\n💡 Попробуйте еще раз.",
                    color=0xed4245
                )
                add_timestamp(embed)
                await interaction.response.edit_message(embed=embed, view=self)
        
        channel_select.callback = channel_select_callback
        self.add_item(channel_select)
        
        back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary, row=1)
        back_btn.callback = lambda i: set_specific(self, i)
        self.add_item(back_btn)
        
        embed = discord.Embed(
            title=f"{get_feature_emoji(feature)} Настройка функции",
            description=f"Настраиваем канал для: **{get_feature_name(feature)}**\n\n"
                       f"Выберите канал, куда будут отправляться уведомления этого типа.",
            color=0x5865f2
        )
        add_timestamp(embed)
        await interaction.response.edit_message(embed=embed, view=self)
    
    func_select.callback = func_select_callback
    self.add_item(func_select)
    
    back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary, row=1)
    back_btn.callback = lambda i: self.show_main_menu(i)
    self.add_item(back_btn)
    
    embed = discord.Embed(
        title="🎯 Индивидуальная настройка функций",
        description="Выберите функцию для настройки отдельного канала логов.\n"
                   "Это позволит разделить разные типы уведомлений по разным каналам.",
        color=0x5865f2
    )
    add_timestamp(embed)
    await interaction.response.edit_message(embed=embed, view=self)


async def view_settings(self, interaction: discord.Interaction):
    """Просмотр текущих настроек"""
    guild_id = self.guild.id
    self.clear_items()
    
    log_channels = self.config.get_guild_log_channels(guild_id)
    if not log_channels:
        embed = discord.Embed(
            title="📋 Текущие настройки логов",
            description="❌ **Каналы для логов пока не настроены.**\n\n"
                       "💡 Используйте кнопки для быстрой настройки!",
            color=0xff6b6b
        )
    else:
        description = "✅ **Активные настройки каналов:**\n\n"
        
        for func, channel_id in log_channels.items():
            channel = self.guild.get_channel(channel_id)
            emoji = get_feature_emoji(func)
            name = get_feature_name(func)
            if channel:
                description += f"{emoji} **{name}:** {channel.mention}\n"
            else:
                description += f"{emoji} **{name}:** ⚠️ Канал не найден (ID: {channel_id})\n"

        embed = discord.Embed(
            title="📊 Текущие настройки логов",
            description=description,
            color=0x4ecdc4
        )
        
        stats = self.config.get_guild_stats(guild_id)
        embed.add_field(
            name="📈 Статистика",
            value=f"🎯 Настроено функций: **{stats['configured_functions']}**\n"
                  f"📁 Уникальных каналов: **{stats['unique_channels']}**",
            inline=True
        )
        
    back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
    back_btn.callback = lambda i: self.show_main_menu(i)
    self.add_item(back_btn)
    
    add_timestamp(embed)
    await interaction.response.edit_message(embed=embed, view=self)


async def clear_all(self, interaction: discord.Interaction):
    """Очистка всех настроек"""
    embed = discord.Embed(
        title="⚠️ Подтверждение очистки",
        description="**ВНИМАНИЕ!** Вы собираетесь удалить ВСЕ настройки каналов логов.\n\n"
                   "❌ Это действие **необратимо**!\n"
                   "🔄 После очистки потребуется заново настраивать все каналы.",
        color=0xff4757
    )
    embed.add_field(
        name="📝 Для подтверждения:",
        value="Введите точно: **KaradevMyGod**",
        inline=False
    )
    add_timestamp(embed)
    
    modal = ClearLogsModal(self, self.config)
    await interaction.response.send_modal(modal) 