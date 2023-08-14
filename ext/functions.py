import json

import discord
from discord.ext import commands
from discord.utils import escape_markdown

from ext import embeds

async def set_guild_invites(bot: commands.Bot, guild: discord.Guild):
    with open('config/guild_settings.json', 'r', encoding='utf-8') as json_file:
        settings = json.load(json_file)

    if str(guild.id) in settings:
        bot.guild_settings[guild.id] = settings[str(guild.id)]

        try:
            bot.guild_settings[guild.id]['invites'] = await guild.invites()
        except discord.Forbidden:
            bot.guild_settings[guild.id]['invites'] = []
            bot.logger.warning('not tracking invites for guild %s %s - Missing Permissions', guild, guild.id)

    else:
        bot.logger.warning('logging disabled for guild %s %s - No Settings', guild, guild.id)


def get_username(user_object: discord.abc.User):
    if isinstance(user_object, discord.Member):
        return escape_markdown(str(user_object._user)) #pylint: disable=protected-access
    else:
        return escape_markdown(str(user_object))

def guild_check(bot: commands.Bot, guild_id: int):
    if guild_id in bot.guild_settings:
        return True
    else:
        return False

async def log_event(
    bot: commands.Bot,
    log_type: dict,
    user: discord.abc.User,
    message: str = None,
    footer: str = None,
    moderator: str = None
):
    if log_type['enabled'] is False:
        return

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
    if log_type['enabled'] is False:
        return

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
    total_seconds = int(delta.total_seconds())
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
