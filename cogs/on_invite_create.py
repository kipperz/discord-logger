import discord
from discord.ext import commands

from ext.functions import set_guild_invites


class OnInviteCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        await set_guild_invites(bot=self.bot, guild=invite.guild)

async def setup(bot: commands.Bot):
    await bot.add_cog(OnInviteCreate(bot))
