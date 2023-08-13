from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord.utils import escape_markdown

from ext import functions


class ModeratorActions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        guild_id = entry.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        if entry.action == discord.AuditLogAction.kick:
            target = await self.bot.fetch_user(entry.target.id)
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['kick'],
                user = target,
                message = entry.reason,
                moderator = entry.user
            )
            # Code in progress to edit the part message to indicate member was kicked
            #
            # part_chan = self.bot.get_channel(settings.PART_LOG)
            # async for message in part_chan(limit=5):
            #     if settings.PART_LOG.message_format == 'text':
            #         if message.content.startswith(f'`{settings.PART_LOG.label.upper()}` {target.mention} `{str(target)}`'):
            #             content = f'{message.content} | Kicked by {entry.user.mention}'
            #             if entry.reason is not None:
            #                 content = f'{content} for {entry.reason}'
            #             await message.edit(content=content)
            #     elif settings.PART_LOG.message_format == 'simple':
            #         if message.embeds:
            #             if f'`{settings.PART_LOG.label.upper()}` {target.mention} `{str(target)}`' in message.embeds[0].description:
            #                 description = f'{message.embeds[0].description} | Kicked by {entry.user.mention}'
            #                 if entry.reason is not None:
            #                     description = f'{description} for {entry.reason}'

            #                 await message.edit(embed=functions.create_embed(description=description))
            #     elif settings.PART_LOG.message_format == 'extended':
            #         if message.embeds:
            #             pass

        elif entry.action in (discord.AuditLogAction.ban, discord.AuditLogAction.unban):
            target = await self.bot.fetch_user(entry.target.id)
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['ban'],
                user = target,
                message = entry.reason,
                moderator = entry.user
            )

        elif entry.action == discord.AuditLogAction.member_update:
            if hasattr(entry.after, 'timed_out_until'):
                if entry.before.timed_out_until is None:
                    await functions.log_event(
                        bot = self.bot,
                        log_type = self.bot.guild_settings[guild_id]['timeout'],
                        user = entry.target,
                        message = functions.timeout_description(entry),
                        moderator = entry.user
                    )
                elif entry.before.timed_out_until < datetime.now(timezone.utc):
                    await functions.log_event(
                        bot = self.bot,
                        log_type = self.bot.guild_settings[guild_id]['timeout'],
                        user = entry.target,
                        message = functions.timeout_description(entry),
                        moderator = entry.user
                    )
                elif entry.after.timed_out_until is None:
                    await functions.log_event(
                        bot = self.bot,
                        log_type = self.bot.guild_settings[guild_id]['timeout'],
                        user = entry.target,
                        message = 'Removed',
                        moderator = entry.user
                    )
                else:
                    await functions.log_event(
                        bot = self.bot,
                        log_type = self.bot.guild_settings[guild_id]['timeout'],
                        user = entry.target,
                        message = f'Updated {functions.timeout_description(entry)}',
                        moderator = entry.user
                    )
            elif hasattr(entry.after, 'deaf'):
                deafen_after = getattr(entry.after, 'deaf', None)
                if deafen_after is True:
                    message = f'deafened {entry.target.mention} `{entry.target}`'
                else:
                    message = f'undeafened {entry.target.mention} `{entry.target}`'

                await functions.log_event(
                    bot = self.bot,
                    log_type = self.bot.guild_settings[guild_id]['voice'],
                    user = entry.user,
                    message = message,
                )
            elif hasattr(entry.after, 'mute') or hasattr(entry.after, 'deafen'):
                mute_after = getattr(entry.after, 'mute', None)
                if mute_after is True:
                    message = f'muted {entry.target.mention} `{entry.target}`'
                else:
                    message = f'unmuted {entry.target.mention} `{entry.target}`'

                await functions.log_event(
                    bot = self.bot,
                    log_type = self.bot.guild_settings[guild_id]['voice'],
                    user = entry.user,
                    message = message,
                )
            elif hasattr(entry.after, 'nick'):
                old_nick = getattr(entry.before, 'nick', None)
                new_nick = getattr(entry.after, 'nick', None)
                target = f'{entry.target.mention} `{entry.target._user}`' #pylint: disable=protected-access

                if old_nick is None and new_nick is not None:
                    message = f'set nickname for {target} to **{escape_markdown(new_nick)}**'
                if old_nick is not None and new_nick is None:
                    message = f'removed nickname **{escape_markdown(old_nick)}** from {target}'
                if old_nick is not None and new_nick is not None:
                    message = f'changed nickname for {target} from **{escape_markdown(old_nick)}** to **{escape_markdown(new_nick)}**'

                await functions.log_event(
                    bot = self.bot,
                    log_type = self.bot.guild_settings[guild_id]['moderator_nick'],
                    user = entry.user,
                    message = message,
                )

        elif entry.action == discord.AuditLogAction.message_delete:
            if entry.user.bot:
                return

            message = f'deleted {entry.extra.count} message(s) in **#{entry.extra.channel.name}** `{entry.extra.channel.id}` sent by {entry.target.mention} `{(entry.target._user)}`' #pylint: disable=protected-access
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['moderator_delete'],
                user = entry.user,
                message = message,
            )

        elif entry.action == discord.AuditLogAction.member_move:
            message = f'{entry.extra.count} member(s) were moved to **#{entry.extra.channel.name}** `{entry.extra.channel.id}`'
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['voice'],
                user = entry.user,
                message = message,
            )

        elif entry.action == discord.AuditLogAction.member_disconnect:
            message = f'disconnected {entry.extra.count} member(s)'
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['moderator_disconnect'],
                user = entry.user,
                message = message,
            )

        elif entry.action == discord.AuditLogAction.member_role_update:
            if entry.user.bot:
                return

            after_roles = []
            for role in entry.after:
                after_roles.append(role.mention)
            before_roles = []
            for role in entry.before:
                before_roles.append(role.mention)

            target = f'{entry.target.mention} `{(entry.target._user)}`' #pylint: disable=protected-access
            if after_roles:
                message = f'removed {len(after_roles)} role(s) from {target}: {", ".join(after_roles)}'
            elif before_roles:
                message = f'granted {target} {len(before_roles)} role(s): {", ".join(after_roles)}'

            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['moderator_role'],
                user = entry.user,
                message = message,
            )

        elif entry.action == discord.AuditLogAction.message_pin:
            jump_url = f'https://discord.com/channels/{entry.guild.id}/{entry.extra.channel.id}/{entry.extra.message_id}'
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['pin'],
                user = entry.user,
                message = f'pinned message: {jump_url}',
            )

        elif entry.action == discord.AuditLogAction.message_unpin:
            jump_url = f'https://discord.com/channels/{entry.guild.id}/{entry.extra.channel.id}/{entry.extra.message_id}'
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['pin'],
                user = entry.user,
                message = f'unpinned message: {jump_url}',
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(ModeratorActions(bot))
