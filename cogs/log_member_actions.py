import discord
from discord.ext import commands
from discord.utils import escape_markdown

from ext import functions


class MemberActions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        guild_id = after.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        if before._user != after._user: #pylint: disable=protected-access
            message = f'from **{escape_markdown(before._user)}** to **{escape_markdown(after._user)}**' #pylint: disable=protected-access
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['username'],
                user = after,
                message = message,
            )

        elif before.nick != after.nick:
            if before.nick is None and after.nick is not None:
                message = f'set nick to **{escape_markdown(after.nick)}**'
            if before.nick is not None and after.nick is None:
                message = f'removed nickname **{escape_markdown(before.nick)}**'
            if before.nick is not None and after.nick is not None:
                message = f'changed nickname from **{escape_markdown(before.nick)}** to **{escape_markdown(after.nick)}**'
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['nick'],
                user = after,
                message = message,
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberActions(bot))
