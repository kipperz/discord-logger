import discord
from discord.ext import commands


class OnInviteCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild_id = invite.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        try:
            self.bot.guild_settings[guild_id] = await invite.guild.invites()
        except discord.Forbidden:
            self.bot.guild_settings[guild_id]['invites'] = []

async def setup(bot: commands.Bot):
    await bot.add_cog(OnInviteCreate(bot))
