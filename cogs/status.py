import discord
from discord.ext import commands, tasks

from config.settings import INVISIBLE_STATUS, CUSTOM_STATUS, CUSTOM_STATUS_DELAY


class CommandsStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.status.start() #pylint: disable=no-member
        self.index = 0

    @tasks.loop(seconds=CUSTOM_STATUS_DELAY)
    async def status(self):
        if CUSTOM_STATUS:
            await self.bot.change_presence(activity=discord.CustomActivity(name=CUSTOM_STATUS[self.index]))
            self.index += 1
            if self.index == len(CUSTOM_STATUS):
                self.index = 0

    @status.before_loop
    async def before_ventures_leaderboard(self):
        await self.bot.wait_until_ready()
        if INVISIBLE_STATUS:
            await self.bot.change_presence(status=discord.Status.offline)

    async def cog_unload(self):
        self.status.cancel() #pylint: disable=no-member

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsStatus(bot))
