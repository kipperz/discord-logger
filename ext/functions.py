import os
import json

import discord
from discord.ext import commands

from ext import embeds


guild_settings_categories = [ 'audit_log',
                              'join_part',
                              'member_actions',
                              'message_log',
                              'moderator_actions',
                              'voice'
                            ]

GUILD_SETTINGS_PATH = 'config/guild_settings.json'

def get_guild_settings():
    if not os.path.exists(GUILD_SETTINGS_PATH):
        guild_settings = {}
        with open(GUILD_SETTINGS_PATH, 'w', encoding='utf-8') as file_pointer:
            file_pointer.write(guild_settings)

    else:
        with open(GUILD_SETTINGS_PATH, 'r', encoding='utf-8') as json_file:
            guild_settings = json.load(json_file)

    return guild_settings

def write_guild_settings(guild_settings):
    with open(GUILD_SETTINGS_PATH, 'w', encoding='utf-8') as file_pointer:
        json.dump(guild_settings, file_pointer, indent=4)

async def set_guild_invites(bot: commands.Bot, guild: discord.Guild):
    guild_settings = get_guild_settings()

    if str(guild.id) in guild_settings:
        bot.guild_settings[guild.id] = guild_settings[str(guild.id)]

        try:
            bot.guild_settings[guild.id]['invites'] = await guild.invites()
            if not bot.connected:
                bot.logger.warning('logging enabled for guild %s %s', guild, guild.id)

        except discord.Forbidden:
            bot.guild_settings[guild.id]['invites'] = []
            if not bot.connected:
                bot.logger.warning('not tracking invites for guild %s %s - Missing Permissions', guild, guild.id)

        if not bot.connected:
            bot.logger.warning('logging enabled for guild %s %s', guild, guild.id)

    elif not bot.connected:
        bot.logger.warning('logging disabled for guild %s %s - No Settings', guild, guild.id)

def enabled_check(bot: commands.Bot, guild_id: int, log_type, channel_id: int = None):
    guild_settings = bot.guild_settings.get(guild_id, None)
    if not guild_settings:
        return False

    if guild_settings[log_type]['disabled']:
        return False

    if channel_id in guild_settings[log_type]['ignore_channels']:
        return False

    return True

async def log_event(
    bot: commands.Bot,
    log_type: dict,
    user: discord.abc.User,
    message: str = None,
    footer: str = None,
    moderator: str = None
):
    channel = bot.get_channel(int(log_type['channel_id']))
    if channel is None:
        bot.logger.error('%s Log channel with ID %s not found', log_type['label'], log_type['channel_id'])
        return

    content, embed = None, None
    if log_type['message_format'] == 'extended':
        embed = embeds.general_log_extended(log_type=log_type, user=user, message=message, footer=footer, moderator=moderator)
    if log_type['message_format'] == 'simple':
        embed = embeds.general_log_simple(log_type=log_type, user=user, message=message, footer=footer, moderator=moderator)
    elif log_type['message_format'] == 'text':
        content = embeds.general_log_text(log_type=log_type, user=user, message=message, footer=footer, moderator=moderator)

    await channel.send(content=content, embed=embed)

async def log_moderator_action( # not logging mod actions
    bot: commands.Bot,
    moderator: discord.Member,
    log_type: dict,
    message: str,
):
    channel = bot.get_channel(int(log_type['channel_id']))
    if channel is None:
        bot.logger.error('%s Log channel with ID %s not found', log_type['label'], log_type['channel_id'])
        return

    content, embed = None, None
    if log_type['message_format'] == 'extended':
        embed = embeds.moderator_action_log_extended(log_type=log_type, moderator=moderator, message=message)
    if log_type['message_format'] == 'simple':
        embed = embeds.moderator_action_log_simple(log_type=log_type, moderator=moderator, message=message)
    elif log_type['message_format'] == 'text':
        content = embeds.moderator_action_log_text(log_type=log_type, moderator=moderator, message=message)

    await channel.send(content=content, embed=embed)

def human_readable_timedelta(delta):
    days = delta.days
    weeks, days = divmod(days, 7)
    total_seconds = round(delta.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    def format_unit(value, unit):
        return f"{value} {unit}" if value == 1 else f"{value} {unit}S"

    if weeks > 0:
        weeks_str = format_unit(weeks, "WEEK")
        if days > 0:
            days_str = format_unit(days, "DAY")
            return f"{weeks_str}, {days_str}"
        return weeks_str
    elif days > 0:
        return format_unit(days, "DAY")
    elif hours > 0:
        hours_str = format_unit(hours, "HOUR")
        minutes_str = format_unit(minutes, "MIN")
        if minutes > 0:
            return f"{hours_str}, {minutes_str}"
        return hours_str
    elif total_seconds == 60:  # Exactly 1 minute
        return format_unit(total_seconds, "SEC")
    elif minutes > 0:
        return format_unit(minutes, "MIN")
    else:
        return format_unit(seconds, "SEC")

def pagination(view, button):
    for item in view.children:
        if item == button:
            item.disabled = True
        else:
            item.disabled = False
