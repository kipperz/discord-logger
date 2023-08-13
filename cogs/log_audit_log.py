import discord
from discord.ext import commands

from ext import audit_log


class AuditLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        guild_id = entry.guild.id
        if guild_id not in self.bot.guild_settings:
            return

        audit_log.database_insert_audit_log_entry(entry)
        await audit_log.log_audit_log_entry(self.bot, entry, self.bot.guild_settings[guild_id]['audit'])

async def setup(bot: commands.Bot):
    await bot.add_cog(AuditLog(bot))
