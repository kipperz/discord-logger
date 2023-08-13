import discord
from discord.ext import commands


class OnAutoModAction(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_auto_mod_action(self, guild: discord.Guild, user: discord.User):
        if guild.id not in self.bot.guild_settings:
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(OnAutoModAction(bot))
