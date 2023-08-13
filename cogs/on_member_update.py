import discord
from discord.ext import commands
from discord.utils import escape_markdown

from ext.functions import log_event


class OnMemberUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        guild_id = after.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        if before.nick != after.nick:
            pass
            # await log_event(
            #     bot = self.bot,
            #     log_type = self.bot.guild_settings[guild_id]['nick'],
            #     user = after,
            #     message = f'From: {escape_markdown(before.nick)} to {escape_markdown(after.nick)}'
            # )

        if before.guild_avatar != after.guild_avatar:
            pass

        elif before.roles != after.roles:
            role = list(set(before.roles) ^ set(after.roles))[0]
            if len(before.roles) < len(after.roles):
                action = 'added'
            else:
                action = 'removed'

            await log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['role'],
                user = after,
                message = f'{role.mention} {action}'
            )

        elif before.pending != after.pending:
            await log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['pending'],
                user = after,
                message = f'{role.mention} {action}'
            )

        elif before.flags.bypasses_verification != after.flags.bypasses_verification:
            pass

        elif before.flags.started_onboarding != after.flags.started_onboarding:
            await log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['onboarding'],
                user = after,
                message = 'started'
            )

        elif before.flags.completed_onboarding != after.flags.completed_onboarding:
            await log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['onboarding'],
                user = after,
                message = 'completed'
            )

        # elif before.is_timed_out() is True and after.is_timed_out() is False:
        #     if before.timed_out_until > datetime.now(timezone.utc):
        #         async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
        #             if entry.target != after:
        #                 continue

        #             elif hasattr(entry.before, 'timed_out_until'):
        #                 if entry.after.timed_out_until is None:
        #                     moderator = entry.user
        #                     break

        #         await log_event(self.bot, settings.TIMEOUT_LOG, after.id, after, f'Removed by {moderator.mention}')

        #     else:
        #         print('timeout expired')

        # elif before.is_timed_out() is True and before.timeout != after.timeout:
        #     async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
        #         if entry.target != after:
        #             continue

        #         elif hasattr(entry.after, 'timed_out_until'):
        #             if entry.after.timed_out_until is not None:
        #                 moderator = entry.user
        #                 timestamp = entry.after.timed_out_until.timestamp()
        #                 if entry.reason is not None:
        #                     reason = f'| {entry.reason} '
        #                 else:
        #                     reason = ''
        #                 break

        #     await log_event(self.bot, settings.TIMEOUT_LOG, after.id, after, f'<t:{int(timestamp)}:d> <t:{int(timestamp)}:t> {reason}| Updated by {moderator.mention}')

        # elif before.timeout != after.timeout:
        #     async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
        #         if entry.target != after:
        #             continue

        #         elif hasattr(entry.after, 'timed_out_until'):
        #             if entry.after.timed_out_until is not None:
        #                 moderator = entry.user
        #                 timestamp = entry.after.timed_out_until.timestamp()
        #                 if entry.reason is not None:
        #                     reason = f'| {entry.reason} '
        #                 else:
        #                     reason = ''
        #                 break

        #     await log_event(self.bot, settings.TIMEOUT_LOG, after.id, after, f'<t:{int(timestamp)}:d> <t:{int(timestamp)}:t> {reason}| Issued by {moderator.mention}')

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberUpdate(bot))
