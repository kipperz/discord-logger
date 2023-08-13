import discord
from discord.ext import commands

from ext import functions


class VoiceLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild_id = member.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        if before.channel is None and after.channel is not None:
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['voice'],
                user = member,
                message = f'joined {after.channel.mention}'
            )

        elif before.channel is not None and after.channel is None:
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['voice'],
                user = member,
                message = f'left {after.channel.mention}'
            )

        elif before.channel is not None and after.channel is not None:
            await functions.log_event(
                bot = self.bot,
                log_type = self.bot.guild_settings[guild_id]['voice'],
                user = member,
                message = f'moved from {before.channel.mention} to {after.channel.mention}'
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceLog(bot))
