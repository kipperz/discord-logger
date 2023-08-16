import discord
from discord.ext import commands

from ext import functions


class JoinPart(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        log_type = 'rejoin' if member.flags.did_rejoin else 'join'
        if not functions.enabled_check(bot=self.bot, guild_id=member.guild.id, log_type=log_type):
            return

        message, footer = await self.guild_invite_compare(member.guild)
        await self.log_join_part(log_type=log_type, member=member, message=message, footer=footer)

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent):
        log_type = 'part'
        if not functions.enabled_check(bot=self.bot, guild_id=payload.guild_id, log_type=log_type):
            return

        await self.log_join_part(log_type=log_type, member=payload.user)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        await functions.set_guild_invites(bot=self.bot, guild=invite.guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        await functions.set_guild_invites(bot=self.bot, guild=invite.guild)

    async def log_join_part(self, log_type: str, member: discord.User, message: str = None, footer: str = None):
        await functions.log_event(
            bot = self.bot,
            log_type = self.bot.guild_settings[member.guild.id][log_type],
            user = member,
            message = message,
            footer = footer
        )

    async def guild_invite_compare(self, guild: discord.Guild):
        # What if the invite is the last invite - is it deleted and cal on_invite_delete?
        message, footer = None, None
        before_invites = self.bot.guild_settings[guild.id].get('invites', [])
        before_dict = {invite.code: invite.uses for invite in before_invites}

        try:
            after_invites = await guild.invites()
        except discord.Forbidden:
            after_invites = []

        if after_invites:
            self.bot.guild_settings[guild.id]['invites'] = after_invites

            for after in after_invites:
                before_uses = before_dict.get(after.code)
                if before_uses is not None and before_uses < after.uses:
                    message = f'Invited by: {after.inviter.mention} `{after.inviter}`'
                    footer = f'Invite: {after.code}'
                    break

        return message, footer

async def setup(bot: commands.Bot):
    await bot.add_cog(JoinPart(bot))
