"""
Интерактивные кнопки для настройки логов
"""

import discord
from discord.ui import View, Button, Select
from ..config import ConfigManager
from ..utils.helpers import add_timestamp, get_feature_emoji, get_feature_name
from .modals import ClearLogsModal


class LogButtons(View):
    """Класс интерактивных кнопок для настройки логов"""
    
    def __init__(self, guild: discord.Guild, config_manager: ConfigManager):
        super().__init__(timeout=300)
        self.guild = guild
        self.config = config_manager
        self.current_page = "main"
        self.message = None
        self.add_main_buttons()
    
    async def on_timeout(self):
        """Обработка истечения времени"""
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="⏰ Время истекло",
            description="🔒 **Интерфейс управления логами закрыт.**\n\n"
                       "💡 Используйте `!setlog-new` для открытия нового интерфейса.",
            color=0x747f8d
        )
        add_timestamp(embed)
        
        try:
            await self.message.edit(embed=embed, view=self)
        except:
            pass
    
    def get_main_embed(self) -> discord.Embed:
        """Создает главный embed"""
        embed = discord.Embed(
            title="🎛️ Панель управления логами",
            description="**Добро пожаловать в центр управления системой логирования!**\n\n"
                       "🚀 Здесь вы можете настроить, куда бот будет отправлять уведомления о различных событиях на сервере.",
            color=0x7289da
        )
        
        embed.add_field(
            name="⚡ Быстрый старт",
            value="Используйте **🌐 Настроить для ВСЕХ функций** для мгновенной настройки!",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Индивидуальная настройка",
            value="Выберите **🎯 Настроить отдельные функции** для точной настройки каждого типа логов.",
            inline=False
        )
        
        embed.add_field(
            name="📊 Мониторинг",
            value="Проверяйте текущие настройки через **📊 Текущие настройки**.",
            inline=False
        )
        
        embed.set_footer(text="🔧 Тайм-аут интерфейса: 5 минут")
        add_timestamp(embed)
        return embed
    
    def add_main_buttons(self) -> None:
        """Добавляет основные кнопки главного меню"""
        self.clear_items()
        
        set_all_btn = Button(
            label="🌐 Настроить для ВСЕХ функций", 
            style=discord.ButtonStyle.success, 
            emoji="⚡", 
            row=0
        )
        set_all_btn.callback = self.set_all
        
        set_specific_btn = Button(
            label="🎯 Настроить отдельные функции", 
            style=discord.ButtonStyle.primary, 
            emoji="⚙️", 
            row=0
        )
        set_specific_btn.callback = self.set_specific
        
        view_settings_btn = Button(
            label="📊 Текущие настройки", 
            style=discord.ButtonStyle.secondary, 
            emoji="📋", 
            row=1
        )
        view_settings_btn.callback = self.view_settings
        
        clear_all_btn = Button(
            label="🗑️ Очистить настройки", 
            style=discord.ButtonStyle.danger, 
            emoji="⚠️", 
            row=1
        )
        clear_all_btn.callback = self.clear_all
        
        self.add_item(set_all_btn)
        self.add_item(set_specific_btn)
        self.add_item(view_settings_btn)
        self.add_item(clear_all_btn)
    
    async def show_main_menu(self, interaction: discord.Interaction):
        """Показывает главное меню"""
        self.current_page = "main"
        self.add_main_buttons()
        
        embed = self.get_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def set_all(self, interaction: discord.Interaction):
        """Настройка одного канала для всех функций"""
        self.current_page = "select_all"
        self.clear_items()
        
        options = [
            discord.SelectOption(label=f"#{channel.name}", value=str(channel.id), emoji="📁")
            for channel in self.guild.text_channels[:25]
        ]
        
        select = Select(placeholder="📁 Выберите канал для всех функций...", options=options)
        
        async def select_callback(interaction: discord.Interaction):
            try:
                channel_id = int(select.values[0])
                channel = self.guild.get_channel(channel_id)
                
                if channel:
                    guild_id = self.guild.id
                    print(f"[DEBUG] Глобальная настройка для сервера {guild_id}")
                    
                    self.config.set_all_channels_for_guild(guild_id, channel_id)
                    
                    embed = discord.Embed(
                        title="✅ Глобальная настройка завершена!",
                        description=f"🎉 **Канал {channel.mention} настроен для ВСЕХ функций!**\n\n"
                                   f"🌐 Теперь все уведомления бота будут приходить в этот канал.\n"
                                   f"💾 Настройки автоматически сохранены!",
                        color=0x57f287
                    )
                    
                    enabled_features = self.config.get_enabled_features()
                    features_text = "\n".join([
                        f"{get_feature_emoji(feat)} {get_feature_name(feat)}" 
                        for feat in enabled_features
                    ])
                    
                    embed.add_field(
                        name="📋 Настроенные функции:",
                        value=features_text,
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
                print(f"Ошибка в select_callback: {e}")
                embed = discord.Embed(
                    title="❌ Произошла ошибка!",
                    description="🚫 **Не удалось настроить канал.**\n\n💡 Попробуйте еще раз.",
                    color=0xed4245
                )
                add_timestamp(embed)
                await interaction.response.edit_message(embed=embed, view=self)
        
        select.callback = select_callback
        self.add_item(select)
        
        back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary, row=1)
        back_btn.callback = lambda i: self.show_main_menu(i)
        self.add_item(back_btn)
        
        embed = discord.Embed(
            title="🌐 Быстрая настройка для всех функций",
            description="Выберите канал, который будет использоваться для **всех** типов логов.\n"
                       "Это самый простой способ настроить бота!",
            color=0x00ff88
        )
        embed.add_field(
            name="📝 Что будет настроено:",
            value="• Приглашения и участники\n• Голосовая активность\n• Сообщения\n• Роли и каналы\n• Баны и муты\n• И многое другое!",
            inline=False
        )
        add_timestamp(embed)
        await interaction.response.edit_message(embed=embed, view=self)
    
    from .log_buttons_methods import set_specific, view_settings, clear_all 