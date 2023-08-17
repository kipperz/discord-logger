import discord
from discord.ext import commands
from discord.utils import escape_markdown

from ext import functions


class MemberActions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        log_type = 'username'

        for guild in after.mutual_guilds:
            if not functions.enabled_check(bot=self.bot, guild_id=guild.id, log_type=log_type):
                return

            message = f'from **{escape_markdown(str(before))}** to **{escape_markdown(str(after))}**'
            if str(before) != str(after):
                await self.log_member_update_event(log_type=log_type, member=after, message=message, guild=guild)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        update_checks = {
            (before.nick, after.nick): lambda: self.nick_handler(before=before, after=after),
            (before.pending, after.pending): lambda: self.log_member_update_event(log_type='pending', member=after, message='verified', guild=after.guild),
            (before.flags.started_onboarding, after.flags.started_onboarding): lambda: self.log_member_update_event(log_type='onboarding', member=after, message='started', guild=after.guild),
            (before.flags.completed_onboarding, after.flags.completed_onboarding): lambda: self.log_member_update_event(log_type='onboarding', member=after, message='completed', guild=after.guild)
        }

        for (before_attr, after_attr), handler in update_checks.items():
            if before_attr != after_attr:
                await handler()
                break

    async def nick_handler(self, before: discord.Member, after: discord.Member):
        log_type='nick'
        if not functions.enabled_check(bot=self.bot, guild_id=after.guild.id, log_type=log_type):
            return

        nick_changes = {
            (False, True): lambda: self.log_member_update_event(log_type=log_type, member=after, message=f'set nick to **{escape_markdown(after.nick)}**', guild=after.guild),
            (True, False): lambda: self.log_member_update_event(log_type=log_type, member=before, message=f'removed nickname **{escape_markdown(before.nick)}**', guild=before.guild),
            (True, True): lambda: self.log_member_update_event(log_type=log_type, member=after, message=f'changed nickname from **{escape_markdown(before.nick)}** to **{escape_markdown(after.nick)}**', guild=after.guild)
        }

        handler = nick_changes[(bool(before.nick), bool(after.nick))]
        if handler:
            await handler()

    async def log_member_update_event(self, log_type: str, member: discord.Member, message: str, guild: discord.Guild):
        if not functions.enabled_check(bot=self.bot, guild_id=guild.id, log_type=log_type):
            return

        if guild is None:
            guild = member.guild

        await functions.log_event(
            bot = self.bot,
            log_type = self.bot.guild_settings[guild.id][log_type],
            user = member,
            message = message
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberActions(bot))
