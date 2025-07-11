"""
Модальные окна для Discord Log Bot
"""

import discord
from discord.ui import Modal, TextInput
from ..config import ConfigManager
from ..utils.helpers import add_timestamp


class ClearLogsModal(Modal, title="⚠️ Подтверждение очистки настроек"):
    """Модальное окно для подтверждения очистки настроек"""
    
    def __init__(self, view, config_manager: ConfigManager):
        super().__init__()
        self.view = view
        self.config = config_manager
        
    confirm = TextInput(
        label="Введите для подтверждения: KaradevMyGod", 
        placeholder="KaradevMyGod",
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirm.value.lower() == "karadevmygod":
            guild_id = interaction.guild.id
            log_channels = self.config.get_guild_log_channels(guild_id)
            
            if log_channels:
                settings_count = len(log_channels)
                self.config.clear_guild_log_channels(guild_id)
                
                embed = discord.Embed(
                    title="✅ Настройки успешно очищены!",
                    description=f"🗑️ **Удалено настроек:** {settings_count}\n\n"
                               f"🔄 Все каналы логов сброшены к значениям по умолчанию.\n"
                               f"💾 Изменения автоматически сохранены!",
                    color=0x57f287
                )
                embed.add_field(
                    name="🎉 Готово!",
                    value="Используйте кнопку **◀️ Назад** для возврата в главное меню.",
                    inline=False
                )
                add_timestamp(embed)
                
                self.view.clear_items()
                back_btn = discord.ui.Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
                back_btn.callback = lambda i: self.view.show_main_menu(i)
                self.view.add_item(back_btn)
                
                await interaction.response.edit_message(embed=embed, view=self.view)
            else:
                embed = discord.Embed(
                    title="ℹ️ Нечего очищать",
                    description="🤷‍♂️ **Настройки каналов логов отсутствуют.**\n\n"
                               f"💡 Сначала настройте каналы логов!",
                    color=0x5865f2
                )
                embed.add_field(
                    name="🎉 Готово!",
                    value="Используйте кнопку **◀️ Назад** для возврата в главное меню.",
                    inline=False
                )
                add_timestamp(embed)
                
                self.view.clear_items()
                back_btn = discord.ui.Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
                back_btn.callback = lambda i: self.view.show_main_menu(i)
                self.view.add_item(back_btn)
                
                await interaction.response.edit_message(embed=embed, view=self.view)
        else:
            embed = discord.Embed(
                title="❌ Очистка отменена",
                description="🛡️ **Настройки НЕ были удалены.**\n\n"
                           f"💡 Неверное подтверждение. Требовалось: **KaradevMyGod**\n"
                           f"📝 Введено: **{self.confirm.value}**",
                color=0xfee75c
            )
            embed.add_field(
                name="🎉 Готово!",
                value="Используйте кнопку **◀️ Назад** для возврата в главное меню.",
                inline=False
            )
            add_timestamp(embed)
            
            self.view.clear_items()
            back_btn = discord.ui.Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
            back_btn.callback = lambda i: self.view.show_main_menu(i)
            self.view.add_item(back_btn)
            
            await interaction.response.edit_message(embed=embed, view=self.view) 