from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands

from ext import database, embeds, functions


class MessageLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # How to handle attachments, stickers, external emojis
    # when checking for mod deletion, match message id not author/channel ids
    # break listeners to separate functions

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            return

        log_type = 'delete'
        if not functions.enabled_check(bot=self.bot, guild_id=message.guild.id, log_type=log_type, channel_id=message.channel.id):
            return

        if not self.pre_checks(message):
            return

        database.database_insert_message(message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if not payload.guild_id:
            return

        log_type = 'delete'
        if not functions.enabled_check(bot=self.bot, guild_id=payload.guild_id, log_type=log_type, channel_id=payload.channel_id):
            return

        timestamp = datetime.now(timezone.utc)

        if payload.cached_message is None:
            message = await database.database_get_last_message(bot=self.bot, guild_id=payload.guild_id, channel_id=payload.channel_id, message_id=payload.message_id)
        else:
            message = payload.cached_message

        if not self.pre_checks(message):
            return

        if hasattr(message.author, 'id'):
            moderator = await self.get_moderator(message)
        else:
            moderator = None

        # ERROR: message.channel = None
        # Union[TextChannel, StageChannel, VoiceChannel, Thread, DMChannel, GroupChannel, PartialMessageable]

        embed = embeds.message_delete_log_extended(message=message, moderator=moderator, timestamp=timestamp)
        await self.send_log(guild_id=payload.guild_id, log_type=log_type, embed=embed)
        database.database_delete_message(message)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if not payload.guild_id:
            return

        log_type = 'edit'
        if not functions.enabled_check(bot=self.bot, guild_id=payload.guild_id, log_type=log_type, channel_id=payload.channel_id):
            return

        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        if not self.pre_checks(message):
            return

        if payload.cached_message is None:
            message_object = await database.database_get_last_message(bot=self.bot, guild_id=payload.guild_id, channel_id=payload.channel_id, message_id=payload.message_id)
            before = message_object.content
        else:
            before = payload.cached_message.content

        if before == message.content or before == "":
            return

        embed = embeds.message_edit_log_extended(message=message, before=before)
        await self.send_log(guild_id=payload.guild_id, log_type=log_type, embed=embed)
        database.database_insert_message(message)

    async def get_moderator(self, message: discord.Message):
        moderator = None
        after = datetime.now(timezone.utc) - timedelta(seconds=5)
        if message.author is not None:
            async for entry in message.guild.audit_logs(after=after, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and entry.extra.channel.id == message.channel.id:
                    moderator = entry.user
                    break
        return moderator

    async def send_log(self, guild_id: int, log_type: str, embed: discord.Embed):
        channel_id = int(self.bot.guild_settings[guild_id][log_type]['channel_id'])
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            self.bot.logger.error('%s Log channel with ID %s not found', self.bot.guild_settings[guild_id][log_type], channel_id)
        else:
            await channel.send(embed=embed)

    def pre_checks(self, message: discord.Message):
        if message.author.bot is True:
            return

        if message.guild is None:
            return

        if message.type not in [discord.MessageType.default, discord.MessageType.reply]:
            return

        if not message.channel:
            return

        return True

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLog(bot))
