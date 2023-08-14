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

        before_channel = before.channel.mention if before.channel else None
        after_channel = after.channel.mention if after.channel else None

        messages = {
            (False, True): f'joined {after_channel}',
            (True, False): f'disconnected from {before_channel}',
            (True, True): f'moved from {before_channel} to {after_channel}',
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
