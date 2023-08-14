import discord
from discord.ext import commands

from ext import functions


class VoiceLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if not functions.guild_check(bot=self.bot, guild_id=member.guild.id):
            return

        messages = {
            (False, True): f'joined {after.channel.mention}',
            (True, False): f'disconnected from {before.channel.mention}',
            (True, True): f'moved from {before.channel.mention} to {after.channel.mention}',
        }
        message = messages[(bool(before.channel), bool(after.channel))]
        await self.log_voice_event(member=member, message=message)

    async def log_voice_event(self, member: discord.Member, message: str):
        await functions.log_event(
            bot = self.bot,
            log_type = self.bot.guild_settings[member.guild.id]['voice'],
            user = member,
            message = message
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceLog(bot))
