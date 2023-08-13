import discord
from discord.ext import commands

from config.settings import log_database


def create_embed(
        title = None,
        description = None,
        color = 0x2b2d31,
        image ='https://cdn.discordapp.com/attachments/683804747337039894/999163953353597009/embed.png',
        author = None,
        author_icon = None,
        footer = None,
        footer_icon = None,
        timestamp = None,
        thumbnail = None,
        url = None,
        fields = []
    ): #pylint: disable=dangerous-default-value

    if description is not None:
        description = ''.join(description)

    discord_embed = discord.Embed(title=title, description=description, url=url, color=color)

    if author is not None:
        discord_embed.set_author(name=author, icon_url=author_icon)

    if fields:
        for field in fields:
            discord_embed.add_field(name=field[0], value=field[1], inline=field[2])

    discord_embed.set_thumbnail(url=thumbnail)

    discord_embed.set_image(url=image)

    if footer is not None:
        discord_embed.set_footer(text=footer, icon_url=footer_icon)

    discord_embed.timestamp = timestamp

    return discord_embed

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

    if log_type['message_format'] == 'extended':
        embed = extended_embed(log_type, user, message, footer, moderator)
        await channel.send(embed=embed)

    if log_type['message_format'] == 'simple':
        embed = simple_embed(log_type, user, message, footer, moderator)
        await channel.send(embed=embed)

    elif log_type['message_format'] == 'text':
        content = text_log(log_type, user, message, footer, moderator)
        await channel.send(content)

def extended_embed( # WIP - do not use
    log_type: dict,
    user: discord.abc.User,
    message: str or None,
    footer: str or None,
    moderator: str or None
):
    description = f'**User:** {user.mention} `{user._user}`' #pylint: disable=protected-access
    if message is not None:
        description = f'{description}\n{message}'
    if moderator is not None:
        description = f'{description}\n\nModerator: {moderator.mention}'
    embed = create_embed(
        author = log_type['label'].upper(),
        author_icon = log_type['icon'],
        description = description,
        thumbnail = user.display_avatar.url,
        footer = footer
    )
    return embed
def simple_embed(
    log_type: dict,
    user: discord.abc.User,
    message: str or None,
    footer: str or None,
    moderator: str or None
):
    log = f'`{log_type["label"].upper()}` {user.mention} `{user._user}`' #pylint: disable=protected-access
    if message is not None:
        log = f'{log} | {message}'

    if moderator is not None:
        log = f'{log} | Moderator: {moderator.mention}'

    embed = create_embed(
        description = log,
        image = None,
        footer = footer
    )
    return embed
def text_log(
    log_type: dict,
    user: discord.abc.User,
    message: str or None,
    footer: str or None,
    moderator: str or None
):
    log = f'`{log_type["label"].upper()}` {user.mention} `{user._user}`' #pylint: disable=protected-access
    if message is not None:
        log = f'{log} | {message}'

    if moderator is not None:
        log = f'{log} | Moderator: {moderator.mention}'

    if footer is not None:
        log = f'{log} | {footer}'

    return log

def database_insert_message(message):
    doc = {
        'message_id': str(message.id),
        'guild_id': str(message.guild.id),
        'channel_id': str(message.channel.id),
        'author': str(message.author),
        'author_id': str(message.author.id),
        'created_at': message.created_at,
        'content': message.content,
        'edited_at': message.edited_at,
        'deleted': False,
    }

    result = log_database[str(message.channel.id)].insert_one(doc)
    if result.inserted_id is not None and result.acknowledged is True:
        pass
    else:
        print('new log not inserted')

def timeout_description(entry):
    description = human_readable_timedelta(entry.after.timed_out_until - entry.created_at)
    if entry.reason is not None:
        description = f'{description} for {entry.reason}'
    return description

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
