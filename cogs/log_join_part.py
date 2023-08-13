import discord
from discord.ext import commands

from ext import functions


class JoinPart(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        message, footer = None, None
        before_invites = self.bot.guild_settings[guild_id].get('invites', [])
        if before_invites:
            try:
                after_invites = await member.guild.invites()
            except discord.Forbidden:
                after_invites = []

            if after_invites:
                self.bot.guild_settings[guild_id]['invites'] = after_invites

                for before, after in zip(before_invites, after_invites):
                    if before.uses < after.uses:
                        message = f'Invited by: {after.inviter.mention} `{after.inviter}`'
                        footer = f'Invite: {after.code}'
                        break

        join_type = 'rejoin' if member.flags.did_rejoin else 'join'
        await functions.log_event(
            bot = self.bot,
            log_type = self.bot.guild_settings[guild_id][join_type],
            user = member,
            message = message,
            footer = footer
        )

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent):
        guild_id = payload.guild_id
        if guild_id not in self.bot.guild_settings:
            return

        await functions.log_event(
            bot = self.bot,
            log_type = self.bot.guild_settings[guild_id]['part'],
            user = payload.user
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(JoinPart(bot))
