#=============================================================================================================#
#                       Этот файл содержит код, который используется в старой версии бота                     #    
#                       Он сохранен для истории и может быть использован в будущем                            #
#=============================================================================================================#
import discord
import json
import os
from discord.ext import commands
from discord.ui import Button, View, Select, Modal, TextInput
from datetime import datetime, timedelta

KaradevFaceKid = commands.Bot(command_prefix="!", intents=discord.Intents.all())

SETTINGS_FILE = "bot_settings.json"

def ensure_settings_file():
    """Создает файл настроек если его нет или он поврежден"""
    default_settings = {
        "enabled_features": {
            "invite_events": True,
            "voice_activity": True,
            "message_events": True,
            "role_events": True,
            "channel_events": True,
            "ban_events": True,
            "timeout_events": True,
            "role_management": True,
        },
        "guild_settings": {}
    }
    
    if not os.path.exists(SETTINGS_FILE):
        print("Создаем новый файл настроек")
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=2)
        return default_settings
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("Файл настроек пустой, создаем новый")
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, ensure_ascii=False, indent=2)
                return default_settings
            
            data = json.loads(content)
            
            # Проверяем структуру и дополняем недостающие поля
            if "enabled_features" not in data:
                data["enabled_features"] = default_settings["enabled_features"]
            if "guild_settings" not in data:
                data["guild_settings"] = {}
            
            # Дополняем недостающие функции
            for feature in default_settings["enabled_features"]:
                if feature not in data["enabled_features"]:
                    data["enabled_features"][feature] = True
            
            # Сохраняем обновленную структуру
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return data
            
    except (json.JSONDecodeError, Exception) as e:
        print(f"Ошибка загрузки настроек: {e}")
        print("Создаем новый файл настроек")
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=2)
        return default_settings

def get_settings():
    """Получает все настройки из JSON файла"""
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        return ensure_settings_file()

def save_settings(settings):
    """Сохраняет настройки в JSON файл"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        print(f"Настройки сохранены успешно")
    except Exception as e:
        print(f"Ошибка сохранения настроек: {e}")

def get_enabled_features():
    """Получает статус включенных функций"""
    settings = get_settings()
    return settings.get("enabled_features", {})

def set_enabled_feature(feature, enabled):
    """Устанавливает статус функции"""
    settings = get_settings()
    if "enabled_features" not in settings:
        settings["enabled_features"] = {}
    settings["enabled_features"][feature] = enabled
    save_settings(settings)

def get_guild_log_channels(guild_id):
    """Получает настройки каналов логов для конкретного сервера"""
    settings = get_settings()
    guild_id_str = str(guild_id)
    return settings.get("guild_settings", {}).get(guild_id_str, {}).get("log_channels", {})

def set_guild_log_channel(guild_id, feature, channel_id):
    """Устанавливает канал логов для конкретной функции на сервере"""
    settings = get_settings()
    guild_id_str = str(guild_id)
    
    if "guild_settings" not in settings:
        settings["guild_settings"] = {}
    if guild_id_str not in settings["guild_settings"]:
        settings["guild_settings"][guild_id_str] = {}
    if "log_channels" not in settings["guild_settings"][guild_id_str]:
        settings["guild_settings"][guild_id_str]["log_channels"] = {}
    
    settings["guild_settings"][guild_id_str]["log_channels"][feature] = channel_id
    save_settings(settings)
    print(f"[SAVE] Установлен канал {channel_id} для функции {feature} на сервере {guild_id}")

def clear_guild_log_channels(guild_id):
    """Очищает все настройки каналов для сервера"""
    settings = get_settings()
    guild_id_str = str(guild_id)
    
    if "guild_settings" in settings and guild_id_str in settings["guild_settings"]:
        if "log_channels" in settings["guild_settings"][guild_id_str]:
            settings["guild_settings"][guild_id_str]["log_channels"] = {}
            save_settings(settings)
            print(f"[CLEAR] Очищены все каналы логов для сервера {guild_id}")

def remove_guild_log_channel(guild_id, channel_id):
    """Удаляет все настройки для конкретного канала"""
    settings = get_settings()
    guild_id_str = str(guild_id)
    
    if "guild_settings" in settings and guild_id_str in settings["guild_settings"]:
        if "log_channels" in settings["guild_settings"][guild_id_str]:
            log_channels = settings["guild_settings"][guild_id_str]["log_channels"]
            # Удаляем все функции, которые используют этот канал
            to_remove = [func for func, ch_id in log_channels.items() if ch_id == channel_id]
            for func in to_remove:
                del log_channels[func]
            save_settings(settings)
            print(f"[REMOVE] Удален канал {channel_id} из настроек сервера {guild_id}")

# Инициализируем файл настроек при запуске
ensure_settings_file()
invites = {}

def add_timestamp(embed):
    embed.set_footer(text=f"Время события: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

def get_log_channel(guild, feature):
    """Получает канал логов для конкретной функции"""
    log_channels = get_guild_log_channels(guild.id)
    
    if feature in log_channels:
        channel_id = log_channels[feature]
        channel = guild.get_channel(channel_id)
        if channel:
            return channel
    
    # Возвращаем канал по умолчанию если настройка не найдена
    default_channel = guild.system_channel or guild.text_channels[0]
    return default_channel

@KaradevFaceKid.event
async def on_ready():
    print(f'Бот {KaradevFaceKid.user.name} успешно запущен!')
    settings = get_settings()
    guild_count = len(settings.get("guild_settings", {}))
    print(f'Настройки загружены: {guild_count} серверов сохранены')
    await KaradevFaceKid.change_presence(activity=discord.Game(name="с твоим отцом в прятки"))

    for guild in KaradevFaceKid.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except discord.Forbidden:
            print(f"Нет прав на просмотр приглашений на сервере {guild.name}.")
        
        log_channels = get_guild_log_channels(guild.id)
        if log_channels:
            print(f"Сервер {guild.name}: настроено {len(log_channels)} каналов логов")

@KaradevFaceKid.command(name="setlog-old")
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, *args):
    await ctx.message.delete()
    guild_id = ctx.guild.id
    enabled_features = get_enabled_features()
    
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
        log_channels = get_guild_log_channels(guild_id)
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
        log_channels = get_guild_log_channels(guild_id)
        if log_channels:
            clear_guild_log_channels(guild_id)
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
        remove_guild_log_channel(guild_id, channel.id)
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
        for func in enabled_features:
            set_guild_log_channel(guild_id, func, channel.id)
        description = f"Теперь все уведомления будут отправляться в {channel.mention}."
    else:
        set_guild_log_channel(guild_id, feature, channel.id)
        description = f"Теперь уведомления для функции `{feature}` будут отправляться в {channel.mention}."

    embed = discord.Embed(
        title="✅ Канал логов настроен!",
        description=description,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, delete_after=10)

@KaradevFaceKid.command(name="toggle")
@commands.has_permissions(administrator=True)
async def toggle_feature(ctx, feature: str = None):
    enabled_features = get_enabled_features()
    
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
        settings = get_settings()
        for item in enabled_features:
            settings["enabled_features"][item] = True
        save_settings(settings)
        
        embed = discord.Embed(
            title="✅ Все функции включены!",
            description="Все функции бота теперь **включены**.",
            color=discord.Color.green()
        )
        add_timestamp(embed)
        await ctx.send(embed=embed)
        return

    if feature == "off":
        settings = get_settings()
        for item in enabled_features:
            settings["enabled_features"][item] = False
        save_settings(settings)
        
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
    set_enabled_feature(feature, new_state)
    state = "включена" if new_state else "выключена"

    embed = discord.Embed(
        title="✅ Состояние функции изменено!",
        description=f"Функция `{feature}` теперь **{state}**.",
        color=discord.Color.green()
    )
    add_timestamp(embed)
    await ctx.send(embed=embed)


@KaradevFaceKid.event
async def on_invite_create(invite):
    enabled_features = get_enabled_features()
    if enabled_features.get('invite_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('invite_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('invite_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('channel_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('channel_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get("voice_activity", False):
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
    enabled_features = get_enabled_features()
    if not enabled_features.get("message_events", False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('message_events', False):
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
    enabled_features = get_enabled_features()
    
    if enabled_features.get('timeout_events', False):
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

    if enabled_features.get('role_management', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('ban_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('ban_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('role_events', False):
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
    enabled_features = get_enabled_features()
    if enabled_features.get('role_events', False):
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





class ClearLogsModal(Modal, title="⚠️ Подтверждение очистки настроек"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        
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
            log_channels = get_guild_log_channels(guild_id)
            if log_channels:
                settings_count = len(log_channels)
                clear_guild_log_channels(guild_id)
                
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
                back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
                back_btn.callback = lambda i: self.view.show_main_menu(i)
                self.view.add_item(back_btn)
                
                await interaction.response.edit_message(embed=embed, view=self)
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
                back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
                back_btn.callback = lambda i: self.view.show_main_menu(i)
                self.view.add_item(back_btn)
                
                await interaction.response.edit_message(embed=embed, view=self)
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
            back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
            back_btn.callback = lambda i: self.view.show_main_menu(i)
            self.view.add_item(back_btn)
            
            await interaction.response.edit_message(embed=embed, view=self)

class LogButtons(View):
    def __init__(self, guild):
        super().__init__(timeout=300)
        self.guild = guild
        self.current_page = "main"
        self.message = None
        self.add_main_buttons()
    
    async def on_timeout(self):
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
    
    def get_main_embed(self):
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
    
    def add_main_buttons(self):
        """Добавляет основные кнопки главного меню"""
        self.clear_items()
        
        # Создаем кнопки заново
        set_all_btn = Button(label="🌐 Настроить для ВСЕХ функций", style=discord.ButtonStyle.success, emoji="⚡", row=0)
        set_all_btn.callback = self.set_all
        
        set_specific_btn = Button(label="🎯 Настроить отдельные функции", style=discord.ButtonStyle.primary, emoji="⚙️", row=0)
        set_specific_btn.callback = self.set_specific
        
        view_settings_btn = Button(label="📊 Текущие настройки", style=discord.ButtonStyle.secondary, emoji="📋", row=1)
        view_settings_btn.callback = self.view_settings
        
        clear_all_btn = Button(label="🗑️ Очистить настройки", style=discord.ButtonStyle.danger, emoji="⚠️", row=1)
        clear_all_btn.callback = self.clear_all
        
        self.add_item(set_all_btn)
        self.add_item(set_specific_btn)
        self.add_item(view_settings_btn)
        self.add_item(clear_all_btn)
    
    async def show_main_menu(self, interaction):
        self.current_page = "main"
        self.add_main_buttons()
        
        embed = self.get_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def set_all(self, interaction: discord.Interaction):
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
                    enabled_features = get_enabled_features()
                    print(f"[DEBUG] Глобальная настройка для сервера {guild_id}")
                    
                    for func in enabled_features:
                        set_guild_log_channel(guild_id, func, channel_id)
                    
                    embed = discord.Embed(
                        title="✅ Глобальная настройка завершена!",
                        description=f"🎉 **Канал {channel.mention} настроен для ВСЕХ функций!**\n\n"
                                   f"🌐 Теперь все уведомления бота будут приходить в этот канал.\n"
                                   f"💾 Настройки автоматически сохранены!",
                        color=0x57f287
                    )
                    embed.add_field(
                        name="📋 Настроенные функции:",
                        value="🎫 События приглашений\n🎧 Голосовая активность\n💬 События сообщений\n"
                              "🎨 События ролей\n📁 События каналов\n🔨 События банов\n🔇 События мутов\n🎖️ Управление ролями",
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
                    
                    if not interaction.response.is_done():
                        await interaction.response.edit_message(embed=embed, view=self)
                    else:
                        await interaction.edit_original_response(embed=embed, view=self)
                else:
                    embed = discord.Embed(
                        title="❌ Ошибка!",
                        description="🚫 **Канал не найден!**\n\n💡 Попробуйте выбрать канал еще раз.",
                        color=0xed4245
                    )
                    add_timestamp(embed)
                    if not interaction.response.is_done():
                        await interaction.response.edit_message(embed=embed, view=self)
                    else:
                        await interaction.edit_original_response(embed=embed, view=self)
            except Exception as e:
                print(f"Ошибка в select_callback: {e}")
                try:
                    embed = discord.Embed(
                        title="❌ Произошла ошибка!",
                        description="🚫 **Не удалось настроить канал.**\n\n💡 Попробуйте еще раз или используйте команду `!quicklog`.",
                        color=0xed4245
                    )
                    add_timestamp(embed)
                    if not interaction.response.is_done():
                        await interaction.response.edit_message(embed=embed, view=self)
                    else:
                        await interaction.edit_original_response(embed=embed, view=self)
                except:
                    pass
        
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

    async def set_specific(self, interaction: discord.Interaction):
        self.current_page = "select_function"
        self.clear_items()
        
        function_emojis = {
            "invite_events": "🎫", "voice_activity": "🎧", "message_events": "💬",
            "role_events": "🎨", "channel_events": "📁", "ban_events": "🔨",
            "timeout_events": "🔇", "role_management": "🎖️"
        }
        
        function_names = {
            "invite_events": "События приглашений", "voice_activity": "Голосовая активность", 
            "message_events": "События сообщений", "role_events": "События ролей",
            "channel_events": "События каналов", "ban_events": "События банов",
            "timeout_events": "События мутов", "role_management": "Управление ролями"
        }
        
        enabled_features = get_enabled_features()
        options = [
            discord.SelectOption(
                label=function_names[func], 
                value=func,
                emoji=function_emojis[func],
                description=f"Настроить логи для {function_names[func].lower()}"
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
                        
                        set_guild_log_channel(guild_id, feature, channel_id)
                        print(f"[DEBUG] Настройка {feature} для сервера {self.guild.name} изменена на канал {channel_id}")
                        
                        emoji = function_emojis.get(feature, "📝")
                        name = function_names.get(feature, feature)
                        
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
                        
                        if not interaction.response.is_done():
                            await interaction.response.edit_message(embed=embed, view=self)
                        else:
                            await interaction.edit_original_response(embed=embed, view=self)
                    else:
                        embed = discord.Embed(
                            title="❌ Ошибка!",
                            description="🚫 **Канал не найден!**\n\n💡 Попробуйте выбрать канал еще раз.",
                            color=0xed4245
                        )
                        add_timestamp(embed)
                        if not interaction.response.is_done():
                            await interaction.response.edit_message(embed=embed, view=self)
                        else:
                            await interaction.edit_original_response(embed=embed, view=self)
                except Exception as e:
                    print(f"Ошибка в channel_select_callback: {e}")
                    try:
                        embed = discord.Embed(
                            title="❌ Произошла ошибка!",
                            description="🚫 **Не удалось настроить канал.**\n\n💡 Попробуйте еще раз или используйте команду `!quicklog`.",
                            color=0xed4245
                        )
                        add_timestamp(embed)
                        if not interaction.response.is_done():
                            await interaction.response.edit_message(embed=embed, view=self)
                        else:
                            await interaction.edit_original_response(embed=embed, view=self)
                    except:
                        pass
            
            channel_select.callback = channel_select_callback
            self.add_item(channel_select)
            
            back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary, row=1)
            back_btn.callback = lambda i: self.set_specific(i)
            self.add_item(back_btn)
            
            embed = discord.Embed(
                title=f"{function_emojis[feature]} Настройка функции",
                description=f"Настраиваем канал для: **{function_names[feature]}**\n\n"
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
        guild_id = str(self.guild.id)
        self.clear_items()
        
        log_channels = get_guild_log_channels(guild_id)
        if not log_channels:
            embed = discord.Embed(
                title="📋 Текущие настройки логов",
                description="❌ **Каналы для логов пока не настроены.**\n\n"
                           "💡 Используйте кнопки для быстрой настройки!",
                color=0xff6b6b
            )
        else:
            description = "✅ **Активные настройки каналов:**\n\n"
            
            function_emojis = {
                "invite_events": "🎫", "voice_activity": "🎧", "message_events": "💬",
                "role_events": "🎨", "channel_events": "📁", "ban_events": "🔨",
                "timeout_events": "🔇", "role_management": "🎖️"
            }
            
            for func, channel_id in log_channels.items():
                channel = self.guild.get_channel(channel_id)
                emoji = function_emojis.get(func, "📝")
                if channel:
                    description += f"{emoji} **{func}:** {channel.mention}\n"
                else:
                    description += f"{emoji} **{func}:** ⚠️ Канал не найден (ID: {channel_id})\n"

            embed = discord.Embed(
                title="📊 Текущие настройки логов",
                description=description,
                color=0x4ecdc4
            )
            
            embed.add_field(
                name="📈 Статистика",
                value=f"🎯 Настроено функций: **{len(log_channels)}**\n"
                      f"📁 Уникальных каналов: **{len(set(log_channels.values()))}**",
                inline=True
            )
            
        back_btn = Button(label="◀️ Назад", style=discord.ButtonStyle.secondary)
        back_btn.callback = lambda i: self.show_main_menu(i)
        self.add_item(back_btn)
        
        add_timestamp(embed)
        await interaction.response.edit_message(embed=embed, view=self)

    async def clear_all(self, interaction: discord.Interaction):
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
        
        modal = ClearLogsModal(self)
        await interaction.response.send_modal(modal)

@KaradevFaceKid.command(name="setlog-new")
@commands.has_permissions(administrator=True)
async def setlog(ctx):
    view = LogButtons(ctx.guild)
    embed = view.get_main_embed()
    
    embed.set_footer(
        text=f"🔧 Настраивает: {ctx.author.display_name} • Тайм-аут интерфейса: 5 минут",
        icon_url=ctx.author.display_avatar.url
    )
    
    message = await ctx.send(embed=embed, view=view)
    view.message = message


@KaradevFaceKid.command(name="reload")
@commands.has_permissions(administrator=True)
async def reload_settings_command(ctx):
    """Команда для ручной перезагрузки настроек из файла"""
    await ctx.message.delete()
    
    # Заставляем перечитать настройки
    settings = get_settings()
    guild_count = len(settings.get("guild_settings", {}))
    
    embed = discord.Embed(
        title="🔄 Настройки перезагружены!",
        description=f"Настройки успешно перезагружены из файла `{SETTINGS_FILE}`.\n"
                   f"Загружено серверов: **{guild_count}**",
        color=discord.Color.blue()
    )
    add_timestamp(embed)
    await ctx.send(embed=embed, delete_after=10)


@KaradevFaceKid.command(name="quicklog")
@commands.has_permissions(administrator=True)
async def quick_log_setup(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    
    guild_id = ctx.guild.id
    enabled_features = get_enabled_features()
    
    for func in enabled_features:
        set_guild_log_channel(guild_id, func, channel.id)

    embed = discord.Embed(
        title="⚡ Быстрая настройка завершена!",
        description=f"Канал {channel.mention} настроен для всех функций логирования.\n"
                   f"Теперь все уведомления будут приходить сюда!",
        color=discord.Color.green()
    )
    add_timestamp(embed)
    await ctx.send(embed=embed)


if __name__ == "__main__":
    import os
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        token = 'YOUR_TOKEN'
        print("⚠️  Используется токен по умолчанию. Для безопасности используйте переменную DISCORD_TOKEN")
    
    KaradevFaceKid.run(token)
