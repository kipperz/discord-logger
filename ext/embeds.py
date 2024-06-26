from typing import Union

import discord

from ext import get_username


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

def simple_log_message(log_type: dict, user: discord.abc.User, message: Union[str, None], moderator: Union[str, None]):
    log_message = f'`{log_type["label"].upper()}` {user.mention} `{get_username(user_object=user)}`'
    if message is not None:
        log_message += f' | {message}'

    if moderator is not None:
        log_message += f' | Moderator: {moderator.mention}'

    return log_message

def general_log_extended( # WIP - do not use
    log_type: dict,
    user: discord.abc.User,
    message: Union[str, None],
    footer: Union[str, None],
    moderator: Union[str, None]
):
    description = f'**User:** {user.mention} `{get_username(user)}`'
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
def general_log_simple(
    log_type: dict,
    user: discord.abc.User,
    message: Union[str, None],
    footer: Union[str, None],
    moderator: Union[str, None]
):
    log_message = simple_log_message(log_type=log_type, user=user, message=message, moderator=moderator)
    return create_embed(description=log_message, image=None, footer=footer)
def general_log_text(
    log_type: dict,
    user: discord.abc.User,
    message: Union[str, None],
    footer: Union[str, None],
    moderator: Union[str, None]
):
    log_message = simple_log_message(log_type=log_type, user=user, message=message, moderator=moderator)
    if footer is not None:
        log_message += f' | {footer}'

    return log_message

def audit_log_extended(entry: discord.AuditLogEntry, log_type: dict, log_entry_details, user: discord.abc.User):
    embed = create_embed(
        description=f'`{log_type["label"]}` {user} {log_entry_details.action} {log_entry_details.target}',
        footer=entry.id
    )
    return embed
def audit_log_simple(entry: discord.AuditLogEntry, log_type: dict, log_entry_details, user: discord.abc.User):
    embed = create_embed(
        description=f'{user} {log_entry_details.action} {log_entry_details.target}',
        image=None,
        footer=f'Entry Id: {entry.id}'
    )
    return embed
def audit_log_text(entry: discord.AuditLogEntry, log_type: dict, log_entry_details, user: discord.abc.User):
    return f'`{log_type["label"]}: {entry.id}` {user} {log_entry_details.action} {log_entry_details.target}'

def moderator_action_log_extended(
    log_type: dict,
    moderator: discord.Member,
    message: str,
):
    embed = create_embed(
        description=f'{moderator.mention} {message}',
        image=None,
    )
    return embed
def moderator_action_log_simple(
    log_type: dict,
    moderator: discord.Member,
    message: str,
):
    embed = create_embed(
        description=f'{moderator.mention} {message}',
        image=None,
    )
    return embed
def moderator_action_log_text(
    log_type: dict,
    moderator: discord.Member,
    message: str,
):
    return f'{moderator.mention} {message}'

def message_edit_log_extended(message: discord.Message, before: str):
    fields= [
        ['User', f'{message.author.mention}\n{get_username(user_object=message.author, escape_markdown=True)}', True],
        ['Channel', f'{message.channel.mention}\n{message.channel.name}', True],
        ['Created At', f'<t:{int(message.created_at.timestamp())}:d>\n<t:{int(message.created_at.timestamp())}:t>', True],
        ['Original Message', before[:1024], False],
        ['Edited Message', message.content[:1024], False]
    ]

    # '`not cached or logged`' if before is none

    embed = create_embed(
        color=discord.Color.orange(),
        fields=fields,
        footer=message.id,
        timestamp=message.edited_at
    )
    return embed
def message_delete_log_extended(message: discord.Message, moderator: discord.User, timestamp):
    description = [f'Message deleted in **#{discord.utils.escape_markdown(message.channel.name)}**']
    if hasattr(message.author, 'id'):
        author = f'{discord.utils.escape_markdown(message.author.display_name)} - {message.author.id}'
        author_icon = message.author.display_avatar.url
        description.append(f' sent by {message.author.mention}\n')
    else:
        author = None,
        author_icon = None
        description.append('\n')

    if message.created_at is not None:
        description.append(f'**Created at**: <t:{int(message.created_at.timestamp())}:F>\n')

    if moderator is not None:
        description.append(f'**Deleted by**: {moderator.mention}')

    embed = create_embed(
        color=discord.Color.red(),
        author=author,
        author_icon=author_icon,
        description=description,
        fields = [['Deleted Message', message.content[:1023], False]],
        footer=f'Message ID: {message.id}',
        timestamp=timestamp
    )
    return embed
