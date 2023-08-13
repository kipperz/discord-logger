import discord
from discord.ext import commands

from config import settings
from ext.functions import log_event


class OnVoiceStatusUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild_id = member.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        # if before.channel is None and after.channel is not None:  # member joined a voice channel
        #     await log_event(self.bot, settings.VOICE_LOG, member.id, member, f'Joined {after.channel.mention}')

        # elif before.channel is not None and after.channel is None:  # member left a voice channel
        #     await log_event(self.bot, settings.VOICE_LOG, member.id, member, f'Left {before.channel.mention}')

        # elif before.channel is not None and after.channel is not None:  # member moved channels
        #     if before.channel != after.channel:
        #         await log_event(self.bot, settings.VOICE_LOG, member.id, member, f'Moved from {before.channel.mention} to {after.channel.mention}')

async def setup(bot: commands.Bot):
    await bot.add_cog(OnVoiceStatusUpdate(bot))
