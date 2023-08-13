import discord
from discord.ext import commands


class OnBulkMessageDelete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, guild: discord.Guild, user: discord.User = None):
        guild_id = guild.id
        if guild_id not in self.bot.guild_settings:
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(OnBulkMessageDelete(bot))
