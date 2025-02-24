import discord
from discord.ext import commands
from discord.ui import Button, View, Select, Modal, TextInput
from datetime import datetime, timedelta

KaradevFaceKid = commands.Bot(command_prefix="!", intents=discord.Intents.all())

log_channels = {}
invites = {}

enabled_features = {
    "invite_events": True,
    "voice_activity": True,
    "message_events": True,
    "role_events": True,
    "channel_events": True,
    "ban_events": True,
    "timeout_events": True,
    "role_management": True,
}


def add_timestamp(embed):
    embed.set_footer(text=f"Время события: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")


def get_log_channel(guild, feature):
    if guild.id in log_channels and feature in log_channels[guild.id]:
        return guild.get_channel(log_channels[guild.id][feature])

    return guild.system_channel or guild.text_channels[0]


@KaradevFaceKid.event
async def on_ready():
    print(f'Бот {KaradevFaceKid.user.name} успешно запущен!')
    await KaradevFaceKid.change_presence(activity=discord.Game(name="с твоим отцом в прятки"))

    for guild in KaradevFaceKid.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except discord.Forbidden:
            print(f"Нет прав на просмотр приглашений на сервере {guild.name}.")



@KaradevFaceKid.command(name="toggle")
@commands.has_permissions(administrator=True)
async def toggle_feature(ctx, feature: str = None):
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
        for item in enabled_features:
            if not enabled_features[item]:
                enabled_features[item] = True

        embed = discord.Embed(
            title="✅ Все функции включены!",
            description="Все функции бота теперь **включены**.",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await ctx.send(embed=embed)
        return

    if feature == "off":
        for item in enabled_features:
            if enabled_features[item]:
                enabled_features[item] = False

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

    enabled_features[feature] = not enabled_features[feature]
    state = "включена" if enabled_features[feature] else "выключена"

    embed = discord.Embed(
        title="✅ Состояние функции изменено!",
        description=f"Функция `{feature}` теперь **{state}**.",
        color=discord.Color.green()
    )
    add_timestamp(embed)
    await ctx.send(embed=embed)


@KaradevFaceKid.event
async def on_invite_create(invite):
    if enabled_features['invite_events']:
        log_channel = get_log_channel(invite.guild, "invite_events")
        embed = discord.Embed(
            title="🎫 Создано новое приглашение!",
            description=f"**Код приглашения:** {invite.code}\n"
                        f"**Создатель:** {invite.inviter.mention}\n"
                        f"**Срок действия:** {f'{invite.max_age} секунд' if invite.max_age else 'Бессрочно'}\n"
                        f"**Максимальное использование:** {invite.max_uses if invite.max_uses else 'Неограничено'}",
            color=discord.Color.blue()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)

        invites[invite.guild.id] = await invite.guild.invites()


@KaradevFaceKid.event
async def on_member_join(member):
    if enabled_features['invite_events']:
        log_channel = get_log_channel(member.guild, "invite_events")

        new_invites = await member.guild.invites()

        used_invite = None
        for invite in invites.get(member.guild.id, []):
            for new_invite in new_invites:
                if invite.code == new_invite.code and invite.uses < new_invite.uses:
                    used_invite = new_invite
                    break
            if used_invite:
                break

        embed = discord.Embed(
            title="🎉 Новый участник!",
            description=f"Добро пожаловать на сервер, {member.mention}!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Аккаунт создан",
                        value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Участников на сервере",
                        value=member.guild.member_count, inline=False)

        if used_invite:
            embed.add_field(
                name="Использованное приглашение",
                value=f"**Код:** {used_invite.code}\n"
                      f"**Создатель:** {used_invite.inviter.mention}\n"
                      f"**Использований:** {used_invite.uses}",
                inline=False
            )

        add_timestamp(embed)
        await log_channel.send(embed=embed)

        invites[member.guild.id] = new_invites


@KaradevFaceKid.event
async def on_member_remove(member):
    if enabled_features['invite_events']:
        log_channel = get_log_channel(member.guild, "invite_events")

        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "Нет ролей"

        embed = discord.Embed(
            title="🚪 Участник покинул сервер",
            description=f"{member.mention} покинул нас. Мы будем скучать!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Участников на сервере", value=member.guild.member_count, inline=True)
        embed.add_field(name="Роли", value=roles_str, inline=False)
        add_timestamp(embed)

        await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_guild_channel_create(channel):
    if enabled_features['channel_events']:
        channel_type = "📝 текстовый" if isinstance(channel, discord.TextChannel) else "🎤 голосовой"
        log_channel = get_log_channel(channel.guild, 'channel_events')
        embed = discord.Embed(
            title="🎉 Создан новый канал!",
            description=f"**Тип канала:** {channel_type}\n**Название:** {channel.mention}",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_guild_channel_delete(channel):
    if enabled_features['channel_events']:
        channel_type = "📝 текстовый" if isinstance(channel, discord.TextChannel) else "🎤 голосовой"
        log_channel = get_log_channel(channel.guild, 'channel_events')
        embed = discord.Embed(
            title="🗑️ Канал удален!",
            description=f"**Тип канала:** {channel_type}\n**Название:** {channel.name}",
            color=discord.Color.red()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_voice_state_update(member, before, after):
    if enabled_features["voice_activity"]:
        log_channel = get_log_channel(member.guild, 'voice_activity')

        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎧 Пользователь зашел в голосовой канал!",
                description=f"{member.mention} зашел в канал {after.channel.mention}.",
                color=discord.Color.blue()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🚪 Пользователь вышел из голосового канала!",
                description=f"{member.mention} вышел из канала {before.channel.mention}.",
                color=discord.Color.orange()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            embed = discord.Embed(
                title="🔀 Пользователь перешел в другой голосовой канал!",
                description=f"{member.mention} перешел из {before.channel.mention} в {after.channel.mention}.",
                color=discord.Color.purple()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

        if before.self_mute != after.self_mute:
            if after.self_mute:
                embed = discord.Embed(
                    title="🎤 Микрофон выключен!",
                    description=f"{member.mention} выключил микрофон в канале {after.channel.mention}.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="🎤 Микрофон включен!",
                    description=f"{member.mention} включил микрофон в канале {after.channel.mention}.",
                    color=discord.Color.green()
                )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

        if before.self_deaf != after.self_deaf:
            if after.self_deaf:
                embed = discord.Embed(
                    title="🎧 Наушники выключены!",
                    description=f"{member.mention} выключил наушники в канале {after.channel.mention}.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="🎧 Наушники включены!",
                    description=f"{member.mention} включил наушники в канале {after.channel.mention}.",
                    color=discord.Color.green()
                )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

        if not before.self_stream and after.self_stream:
            embed = discord.Embed(
                title="📺 Началась демонстрация экрана!",
                description=f"{member.mention} начал демонстрацию экрана в {after.channel.mention}.",
                color=discord.Color.teal()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

        if before.self_stream and not after.self_stream:
            embed = discord.Embed(
                title="🛑 Демонстрация экрана завершена!",
                description=f"{member.mention} закончил демонстрацию экрана в {after.channel.mention}.",
                color=discord.Color.dark_teal()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)



@KaradevFaceKid.event
async def on_message_delete(message):
    if not enabled_features["message_events"]:
        return

    log_channel = get_log_channel(message.guild, 'message_events')


    embed = discord.Embed(
        title="🗑️ Сообщение удалено!",
        description=f"**Автор:** {message.author.mention}\n"
                    f"**Сообщение:** {message.content}\n",
        color=discord.Color.dark_red()
    )
    add_timestamp(embed)
    await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_message_edit(before, after):
    if enabled_features['message_events']:
        if before.content != after.content:
            log_channel = get_log_channel(before.guild, 'message_events')
            embed = discord.Embed(
                title="✏️ Сообщение отредактировано!",
                description=f"**Автор:** {before.author.mention}\n**Было:** {before.content}\n**Стало:** {after.content}",
                color=discord.Color.gold()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_member_update(before, after):
    if enabled_features['timeout_events']:
        log_channel = get_log_channel(after.guild, 'timeout_events')
        if not before.is_timed_out() and after.is_timed_out():
            timeout_duration = after.timed_out_until - datetime.utcnow()
            timeout_duration = timeout_duration - timedelta(microseconds=timeout_duration.microseconds)
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                moderator = entry.user
                break
            else:
                moderator = "Неизвестный администратор"
            embed = discord.Embed(
                title="🔇 Пользователь получил мут!",
                description=f"{after.mention} был замучен на {timeout_duration}.\n**Администратор:** {moderator.mention}",
                color=discord.Color.orange()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)
        elif before.is_timed_out() and not after.is_timed_out():
            embed = discord.Embed(
                title="🔊 Мут снят!",
                description=f"{after.mention} больше не замучен.",
                color=discord.Color.green()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)


    if enabled_features['role_management']:
        log_channel = get_log_channel(after.guild, 'role_management')
        if len(before.roles) < len(after.roles):
            new_role = next(role for role in after.roles if role not in before.roles)
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
                moderator = entry.user
                break
            else:
                moderator = "Неизвестный администратор"
            embed = discord.Embed(
                title="🎖️ Пользователь получил роль!",
                description=f"{after.mention} получил роль {new_role.mention}.\n**Администратор:** {moderator.mention}",
                color=discord.Color.blue()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)


        elif len(before.roles) > len(after.roles):
            removed_role = next(role for role in before.roles if role not in after.roles)
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
                moderator = entry.user
                break
            else:
                moderator = "Неизвестный администратор"
            embed = discord.Embed(
                title="❌ Пользователь потерял роль!",
                description=f"{after.mention} потерял роль {removed_role.mention}.\n**Администратор:** {moderator.mention}",
                color=discord.Color.red()
            )
            add_timestamp(embed)
            await log_channel.send(embed=embed)

@KaradevFaceKid.event
async def on_member_ban(guild, user):
    if enabled_features['ban_events']:
        log_channel = get_log_channel(guild, 'ban_events')
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            moderator = entry.user
            break
        else:
            moderator = "Неизвестный администратор"
        embed = discord.Embed(
            title="🔨 Пользователь забанен!",
            description=f"{user.mention} был забанен.\n**Администратор:** {moderator.mention}",
            color=discord.Color.red()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_member_unban(guild, user):
    if enabled_features['ban_events']:
        log_channel = get_log_channel(guild, 'ban_events')
        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=1):
            moderator = entry.user
            break
        else:
            moderator = "Неизвестный администратор"
        embed = discord.Embed(
            title="🎉 Пользователь разбанен!",
            description=f"{user.mention} был разбанен.\n"
                        f"**Администратор:** {moderator.mention}",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)

@KaradevFaceKid.event
async def on_guild_role_create(role):
    if enabled_features['role_events']:
        log_channel = get_log_channel(role.guild, 'role_events')

        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            moderator = entry.user
            break
        else:
            moderator = "Неизвестный администратор"

        embed = discord.Embed(
            title="🎨 Создана новая роль!",
            description=f"**Роль:** {role.mention}\n"
                        f"**Цвет:** {str(role.color)}\n"
                        f"**Администратор:** {moderator.mention}",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)


@KaradevFaceKid.event
async def on_guild_role_delete(role):
    if enabled_features['role_events']:
        log_channel = get_log_channel(role.guild, 'role_events')

        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            moderator = entry.user
            break
        else:
            moderator = "Неизвестный администратор"

        embed = discord.Embed(
            title="🗑️ Роль удалена!",
            description=f"**Роль:** @{role.name}\n"
                        f"**Цвет:** {str(role.color)}\n"
                        f"**Администратор:** {moderator.mention}",
            color=discord.Color.red()
        )
        add_timestamp(embed)
        await log_channel.send(embed=embed)



class ChannelSelect(Select):
    def __init__(self, guild, feature):
        self.guild = guild
        self.feature = feature
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in guild.text_channels
        ]
        super().__init__(placeholder="Выберите канал", options=options)

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        channel = self.guild.get_channel(channel_id)
        if channel:
            if self.guild.id not in log_channels:
                log_channels[self.guild.id] = {}
            log_channels[self.guild.id][self.feature] = channel_id
            await interaction.response.send_message(f"Канал для {self.feature} настроен на {channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("Канал не найден!", ephemeral=True)


class ChannelSelectView(View):
    def __init__(self, guild, feature):
        super().__init__()
        self.add_item(ChannelSelect(guild, feature))


class ClearLogsModal(Modal, title="Очистка настроек логов"):
    confirm = TextInput(label="Введите 'KaradevMyGod' для подтверждения", placeholder="KaradevMyGod")

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirm.value.lower() == "KaradevMyGod":
            guild_id = interaction.guild.id
            if guild_id in log_channels:
                log_channels.pop(guild_id)
                await interaction.response.send_message("Все настройки каналов логов были удалены.", ephemeral=True)
            else:
                await interaction.response.send_message("Настройки каналов логов отсутствуют.", ephemeral=True)
        else:
            await interaction.response.send_message("Очистка отменена.", ephemeral=True)

class LogButtons(View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.guild = guild

    @discord.ui.button(label="Настроить канал для всех функций", style=discord.ButtonStyle.green)
    async def set_all(self, interaction: discord.Interaction, button: Button):
        view = ChannelSelectView(self.guild, "all")
        await interaction.response.send_message("Выберите канал для всех функций:", view=view, ephemeral=True)

    @discord.ui.button(label="Настроить канал для конкретной функции", style=discord.ButtonStyle.blurple)
    async def set_specific(self, interaction: discord.Interaction, button: Button):
        options = [
            discord.SelectOption(label=func, value=func)
            for func in enabled_features
        ]
        select = Select(placeholder="Выберите функцию", options=options)

        async def select_callback(interaction: discord.Interaction):
            feature = select.values[0]
            view = ChannelSelectView(self.guild, feature)
            await interaction.response.send_message(f"Выберите канал для функции `{feature}`:", view=view, ephemeral=True)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Выберите функцию:", view=view, ephemeral=True)

    @discord.ui.button(label="Просмотреть текущие настройки", style=discord.ButtonStyle.gray)
    async def view_settings(self, interaction: discord.Interaction, button: Button):
        guild_id = self.guild.id
        if guild_id not in log_channels or not log_channels[guild_id]:
            embed = discord.Embed(
                title="📋 Список каналов логов",
                description="Каналы для логов не настроены.",
                color=discord.Color.blue()
            )
        else:
            description = ""
            for func, channel_id in log_channels[guild_id].items():
                channel = self.guild.get_channel(channel_id)
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
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Очистить все настройки", style=discord.ButtonStyle.red)
    async def clear_all(self, interaction: discord.Interaction, button: Button):
        modal = ClearLogsModal()
        await interaction.response.send_modal(modal)

@KaradevFaceKid.command(name="setlog")
@commands.has_permissions(administrator=True)
async def setlog(ctx):
    view = LogButtons(ctx.guild)
    await ctx.send("Управление настройками каналов логов:", view=view)

KaradevFaceKid.run('Your_Token')