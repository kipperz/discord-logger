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
        async def default_handler(entry):
            pass

        if not functions.guild_check(bot=self.bot, guild_id=entry.guild.id):
            return

        handler_name = f'{entry.action.name.lower()}_handler'
        handler = getattr(self, handler_name, default_handler)
        await handler(entry)

    async def kick_handler(self, entry: discord.AuditLogEntry):
        log_type = 'kick'
        try:
            target = await self.bot.fetch_user(entry.target.id)
        except:
            pass
        message = f'kicked {target.mention} `{functions.get_username(target)}`'
        if entry.reason:
            message += f'| Reason: {entry.reason}'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def ban_handler(self, entry: discord.AuditLogEntry):
        log_type = 'ban'
        target = await self.bot.fetch_user(entry.target.id)
        message = f'banned {target.mention} `{functions.get_username(target)}`'
        if entry.reason:
            message += f'| Reason: {entry.reason}'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def unban_handler(self, entry: discord.AuditLogEntry):
        log_type = 'ban'
        target = await self.bot.fetch_user(entry.target.id)
        message = f'unbanned {target.mention} `{functions.get_username(target)}`'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_update_handler(self, entry: discord.AuditLogEntry):
        attribute_to_handler = {
            'timed_out_until': self.member_time_out,
            'deaf': self.member_deafen,
            'mute': self.member_mute,
            'nick': self.member_nick
        }

        for attr, handler in attribute_to_handler.items():
            if hasattr(entry.after, attr):
                await handler(entry)
                break

    async def member_time_out(self, entry: discord.AuditLogEntry):
        def timeout_length():
            return functions.human_readable_timedelta(entry.after.timed_out_until - entry.created_at)

        log_type = 'timeout'
        member_details = f'{entry.target.mention} `{functions.get_username(entry.target)}`'
        if not entry.before.timed_out_until or entry.before.timed_out_until < datetime.now(timezone.utc):
            message = f'timed out {member_details} for {timeout_length()}'
            if entry.reason:
                message += f'| Reason: {entry.reason}'
            await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)
        elif not entry.after.timed_out_until:
            message = f'removed timed out from {member_details}`'
            await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)
        else:
            message = f'updated timeout for {member_details} to {timeout_length()}'
            if entry.reason:
                message += f'| Reason: {entry.reason}'
            await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_deafen(self, entry: discord.AuditLogEntry):
        log_type = 'deaf'
        deafen_after = getattr(entry.after, 'deaf', None)
        if deafen_after is True:
            message = f'deafened {entry.target.mention} `{functions.get_username(entry.target)}`'
        else:
            message = f'undeafened {entry.target.mention} `{functions.get_username(entry.target)}`'

        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_mute(self, entry: discord.AuditLogEntry):
        log_type = 'mute'
        mute_after = getattr(entry.after, 'mute', None)
        if mute_after is True:
            message = f'muted {entry.target.mention} `{functions.get_username(entry.target)}`'
        else:
            message = f'unmuted {entry.target.mention} `{functions.get_username(entry.target)}`'

        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_nick(self, entry: discord.AuditLogEntry):
        log_type = 'moderator_nick'
        old_nick = getattr(entry.before, 'nick', None)
        new_nick = getattr(entry.after, 'nick', None)
        target = f'{entry.target.mention} `{functions.get_username(entry.target)}`'

        messages = {
            (False, True): f'set nickname for {target} to **{escape_markdown(new_nick)}**',
            (True, False): f'removed nickname **{escape_markdown(old_nick)}** from {target}',
            (True, True): f'changed nickname for {target} from **{escape_markdown(old_nick)}** to **{escape_markdown(new_nick)}**'
        }

        message = messages[(bool(old_nick), bool(new_nick))]
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def message_delete_handler(self, entry: discord.AuditLogEntry):
        if entry.user.bot:
            return

        if isinstance(entry.target, discord.object.Object):
            try:
                target = await self.bot.fetch_user(entry.target.id)
            except discord.errors.NotFound:
                username = 'Deleted User'

            if target is None:
                username = 'Deleted User'
        else:
            username = functions.get_username(entry.target)

        log_type = 'moderator_delete'
        message = f'deleted {entry.extra.count} message(s) in **#{entry.extra.channel.name}** `{entry.extra.channel.id}` sent by <@{entry.target.id}> `{username}`'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_move_handler(self, entry: discord.AuditLogEntry):
        log_type = 'moderator_move'
        message = f'{entry.extra.count} member(s) were moved to **#{entry.extra.channel.name}** `{entry.extra.channel.id}`'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_disconnect_handler(self, entry: discord.AuditLogEntry):
        log_type = 'moderator_disconnect'
        message = f'disconnected {entry.extra.count} member(s)'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def member_role_update_handler(self, entry: discord.AuditLogEntry):
        if entry.user.bot:
            return

        log_type = 'moderator_role'
        after_roles = [role.mention for role in entry.after.roles]
        before_roles = [role.mention for role in entry.before.roles]
        target = f'{entry.target.mention} `{functions.get_username(entry.target)}`'

        if after_roles:
            message = f'removed {len(after_roles)} role(s) from {target}: {", ".join(after_roles)}'
        elif before_roles:
            message = f'granted {target} {len(before_roles)} role(s): {", ".join(before_roles)}'

        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def message_pin_handler(self, entry: discord.AuditLogEntry):
        log_type = 'pin'
        jump_url = f'https://discord.com/channels/{entry.guild.id}/{entry.extra.channel.id}/{entry.extra.message_id}'
        message = f'pinned message: {jump_url}'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def message_unpin_handler(self, entry: discord.AuditLogEntry):
        log_type = 'pin'
        jump_url = f'https://discord.com/channels/{entry.guild.id}/{entry.extra.channel.id}/{entry.extra.message_id}'
        message = f'unpinned message: {jump_url}'
        await self.log_moderator_action_event(moderator=entry.user, log_type=log_type, message=message)

    async def log_moderator_action_event(self, moderator: discord.Member, log_type: str, message: str):
        await functions.log_moderator_action(
            bot = self.bot,
            moderator = moderator,
            log_type = self.bot.guild_settings[moderator.guild.id][log_type],
            message = message
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ModeratorActions(bot))
