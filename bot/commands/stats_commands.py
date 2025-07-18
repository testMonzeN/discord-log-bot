"""
Команды для вывода статистики по ролям, пользователям, сообщениям, приглашениям, голосовой активности, каналам, банам и мьютам Discord-сервера.
"""

import discord
from discord.ext import commands
from bot.analytics.analytics_manager import analytics_manager

class StatsCommands(commands.Cog):
    """
    Команды для получения аналитики по всем ключевым событиям Discord.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='stats')
    async def stats(self, ctx, stat_type: str = None):
        if not stat_type:
            embed = discord.Embed(title='ℹ️ Выберите тип статистики',
                                  description='Укажите тип статистики:\n'
                                  '🎨 role\n'
                                  '👤 users\n'
                                  '💬 message\n'
                                  '🎫 invite\n'
                                  '🎧 voice\n'
                                  '📁 channel\n'
                                  '🔨 ban\n'
                                  '🔇 mute',
                                  color=0x7289da)
            await ctx.send(embed=embed)
            return
        if stat_type == 'role':
            await self.send_role_stats(ctx)
        elif stat_type == 'users':
            await self.send_user_stats(ctx)
        elif stat_type == 'message':
            await self.send_message_stats(ctx)
        elif stat_type == 'invite':
            await self.send_invite_stats(ctx)
        elif stat_type == 'voice':
            await self.send_voice_stats(ctx)
        elif stat_type == 'channel':
            await self.send_channel_stats(ctx)
        elif stat_type == 'ban':
            await self.send_ban_stats(ctx)
        elif stat_type == 'mute':
            await self.send_mute_stats(ctx)
        else:
            embed = discord.Embed(title='❌ Неизвестный тип статистики',
                                  description=(
                                    'Попробуйте одну из команд:\n'
                                    '———————————————\n'
                                    '🎨  `!stats role` — статистика ролей\n'
                                    '👤  `!stats users` — статистика пользователей\n'
                                    '💬  `!stats message` — статистика сообщений\n'
                                    '🎫  `!stats invite` — статистика инвайтов\n'
                                    '🎧  `!stats voice` — статистика войсов\n'
                                    '📁  `!stats channel` — статистика каналов\n'
                                    '🔨  `!stats ban` — статистика банов\n'
                                    '🔇  `!stats mute` — статистика мутов'
                                  ),
                                  color=0xff5555)
            await ctx.send(embed=embed)

    @commands.group(name='restore_analytics', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def restore_analytics(self, ctx, filename: str = None):
        """
        Восстанавливает analytics.json из резервной копии backups/<filename> или выводит список бэкапов.
        """
        import os, shutil
        backup_dir = 'backups'
        if not filename:
            files = os.listdir(backup_dir) if os.path.exists(backup_dir) else []
            if not files:
                embed = discord.Embed(title='❌ Нет доступных резервных копий.', color=0xff5555)
                await ctx.send(embed=embed)
                return
            files = sorted(files, reverse=True)
            embed = discord.Embed(title='📦 Доступные резервные копии',
                                  description='Укажите имя файла для восстановления или используйте `/restore_analytics list` для просмотра всех бэкапов.\n\nДоступные бэкапы:' + '\n' + '\n'.join(f'- `{f}`' for f in files),
                                  color=0x7289da)
            await ctx.send(embed=embed)
            return
        if filename == 'list':
            await self.restore_analytics_list(ctx)
            return
        backup_path = os.path.join(backup_dir, filename)
        if not os.path.exists(backup_path):
            embed = discord.Embed(title='❌ Ошибка', description=f'Файл `{filename}` не найден в папке backups.', color=0xff5555)
            await ctx.send(embed=embed)
            return
        try:
            shutil.copy2(backup_path, 'analytics.json')
            embed = discord.Embed(title='✅ Восстановление завершено', description=f'Файл analytics.json успешно восстановлен из `{filename}`!', color=0x2ecc71)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='❌ Ошибка восстановления', description=str(e), color=0xff5555)
            await ctx.send(embed=embed)

    @restore_analytics.command(name='list')
    async def restore_analytics_list(self, ctx):
        import os
        backup_dir = 'backups'
        files = os.listdir(backup_dir) if os.path.exists(backup_dir) else []
        if not files:
            embed = discord.Embed(title='❌ Нет доступных резервных копий.', color=0xff5555)
            await ctx.send(embed=embed)
            return
        files = sorted(files, reverse=True)
        embed = discord.Embed(title='📦 Список резервных копий аналитики',
                              description='\n'.join(f'- `{f}`' for f in files),
                              color=0x7289da)
        await ctx.send(embed=embed)

    async def send_role_stats(self, ctx):
        data = analytics_manager.data['roles']
        added = sum(data['added'].values())
        removed = sum(data['removed'].values())
        created = data.get('created', 0)
        deleted = data.get('deleted', 0)
        embed = discord.Embed(title='🎨 Статистика по ролям', color=0x3498db)
        value = f"🎖️ Выдано ролей: {added}\n🗑️ Снято ролей: {removed}\n✨ Создано ролей: {created}\n❌ Удалено ролей: {deleted}"
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_user_stats(self, ctx):
        data = analytics_manager.data['users']
        joined = data['joined']
        left = data['left']
        top = sorted(data['top_active'].items(), key=lambda x: x[1], reverse=True)[:5]
        value = f"➕ Вошло пользователей: {joined}\n➖ Покинуло пользователей: {left}"
        if top:
            value += "\n\n🏆 Топ активных:\n" + '\n'.join([f'🏅 <@{uid}>: {count}' for uid, count in top])
        embed = discord.Embed(title='👤 Статистика по пользователям', color=0x2ecc71)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_message_stats(self, ctx):
        data = analytics_manager.data['messages']
        sent = data['sent']
        deleted = data['deleted']
        edited = data['edited']
        top = sorted(data['top_senders'].items(), key=lambda x: x[1], reverse=True)[:5]
        value = f"✉️ Отправлено сообщений: {sent}\n🗑️ Удалено сообщений: {deleted}\n✏️ Отредактировано сообщений: {edited}"
        if top:
            value += "\n\n🏆 Топ отправителей:\n" + '\n'.join([f'🏅 <@{uid}>: {count}' for uid, count in top])
        embed = discord.Embed(title='💬 Статистика по сообщениям', color=0xe67e22)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_invite_stats(self, ctx):
        data = analytics_manager.data['invites']
        created = data['created']
        used = data['used']
        value = f"✨ Создано приглашений: {created}\n✅ Использовано приглашений: {used}"
        embed = discord.Embed(title='🎫 Статистика по приглашениям', color=0x9b59b6)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_voice_stats(self, ctx):
        data = analytics_manager.data['voice']
        join = data['join']
        leave = data['leave']
        mute = data['mute']
        unmute = data['unmute']
        value = f"🔊 Входов в голосовые: {join}\n🚪 Выходов из голосовых: {leave}\n🔇 Мьютов: {mute}\n🔊 Размьютов: {unmute}"
        embed = discord.Embed(title='🎧 Голосовая активность', color=0x1abc9c)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_channel_stats(self, ctx):
        data = analytics_manager.data['channels']
        created = data['created']
        deleted = data['deleted']
        value = f"✨ Создано каналов: {created}\n❌ Удалено каналов: {deleted}"
        embed = discord.Embed(title='📁 Статистика по каналам', color=0xf1c40f)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_ban_stats(self, ctx):
        data = analytics_manager.data['bans']
        banned = data['banned']
        unbanned = data['unbanned']
        value = f"⛔ Банов: {banned}\n✅ Разбанов: {unbanned}"
        embed = discord.Embed(title='🔨 Статистика по банам', color=0xe74c3c)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

    async def send_mute_stats(self, ctx):
        data = analytics_manager.data['mutes']
        timeout = data['timeout']
        untimeout = data['untimeout']
        value = f"⏳ Выдано тайм-аутов: {timeout}\n✅ Снято тайм-аутов: {untimeout}"
        embed = discord.Embed(title='🔇 Статистика по мьютам (тайм-аутам)', color=0x95a5a6)
        embed.add_field(name="", value=value, inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(StatsCommands(bot)) 