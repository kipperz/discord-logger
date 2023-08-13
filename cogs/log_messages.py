from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord.utils import escape_markdown
from pymongo import DESCENDING

from config import settings

from ext import functions


class MessageLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # How to handle attachments, stickers, external emojis
    # when checking for mod deletion, match message id not author/channel ids
    # break listeners to separate functions

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author is self.bot.user:
            return

        guild_id = message.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        if message.type != discord.MessageType.default:
            return

        if message.author.bot is True:
            return

        functions.database_insert_message(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        guild_id = payload.guild_id
        if guild_id not in self.bot.guild_settings:
            return

        if payload.cached_message is None:
            message_doc = settings.log_database[str(payload.channel_id)].find_one({'message_id': str(payload.message_id)}, sort=[('edited_at', DESCENDING)])
            if message_doc is None:
                message_doc = {}
                author_object = None
            else:
                author_object = await self.bot.fetch_user(message_doc['author_id'])

            class message: #pylint: disable=invalid-name
                id = payload.message_id
                author = author_object
                guild = self.bot.get_guild(payload.guild_id)
                channel = guild.get_channel(payload.channel_id)
                created_at = message_doc.get('created_at', None)
                content = message_doc.get('content', None)

        else:
            message = payload.cached_message

            if message.author == self.bot.user:
                return

            if message.type != discord.MessageType.default:
                return

        moderator = None
        if message.author is not None:
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and entry.extra.channel.id == message.channel.id:
                    moderator = entry.user

        if message.author is not None:
            fields = [['User', f'{message.author.mention}\n{escape_markdown(message.author._user)}', True]] #pylint: disable=restricted-access
        else:
            fields = [['User', 'unlogged message', True]]
        fields.append(['Channel', f'{message.channel.mention}\n{message.channel.name}', True])
        if message.created_at is not None:
            fields.append(['Created At', f'<t:{int(message.created_at.timestamp())}:d>\n<t:{int(message.created_at.timestamp())}:t>', True])
        if message.created_at is not None:
            fields.append(['Deleted Message', message.content[:1024], False])

        if moderator is not None:
            fields.append(['Deleted by', moderator.mention, False])

        embed = functions.create_embed(
            color=discord.Color.red(),
            fields=fields,
            footer=message.id,
            timestamp=datetime.now(timezone.utc)
        )
        channel_id = int(self.bot.guild_settings[guild_id]['delete']['channel_id'])
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            self.bot.logger.error('%s Log channel with ID %s not found', self.bot.guild_settings[guild_id]['delete'], channel_id)
        else:
            await channel.send(embed=embed)

        settings.log_database[str(message.channel.id)].update_many({'message_id': str(message.id)}, {'$set': {'deleted': True}})

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        guild_id = payload.guild_id
        if guild_id not in self.bot.guild_settings:
            return

        try:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        except discord.NotFound:
            return

        if message.author.bot:
            return

        if payload.cached_message is None:
            message_doc = settings.log_database[str(payload.channel_id)].find_one({'message_id': str(payload.message_id)}, sort=[('edited_at', DESCENDING)])
            if message_doc is None:
                before = '`not cached or logged`'
            else:
                before = message_doc['content']

        else:
            before = payload.cached_message.content

        fields= [
            ['User', f'{message.author.mention}\n{escape_markdown(message.author._user)}', True]], #pylint: disable=restricted-access
            ['Channel', f'{message.channel.mention}\n{message.channel.name}', True],
            ['Created At', f'<t:{int(message.created_at.timestamp())}:d>\n<t:{int(message.created_at.timestamp())}:t>', True],
            ['Original Message', before[:1024], False],
            ['Edited Message', message.content[:1024], False]
        ]

        embed = functions.create_embed(
            color=discord.Color.orange(),
            fields=fields,
            footer=message.id,
            timestamp=datetime.now(timezone.utc)
        )
        channel_id = int(self.bot.guild_settings[guild_id]['edit']['channel_id'])
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            self.bot.logger.error('%s Log channel with ID %s not found', self.bot.guild_settings[guild_id]['edit'], channel_id)
        else:
            await channel.send(embed=embed)

        functions.database_insert_message(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLog(bot))
