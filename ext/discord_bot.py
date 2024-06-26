import os
from logging import Logger

import discord
from discord.ext import commands

from config import settings
from ext.functions import set_guild_invites


intents = discord.Intents.none()
intents.guild_messages = True
intents.guilds = True
intents.invites = True
intents.members = True
intents.message_content = True
intents.moderation = True
intents.voice_states = True

class DiscordBot(commands.Bot):
    def __init__(self, logger: Logger):
        super().__init__(
            command_prefix = settings.COMMAND_PREFIX,
            intents = intents,
            log_hander = logger,
            application_id = settings.APPLICATION_ID,
        )
        self.connected = False
        self.synced = False
        self.logger = logger
        self.guild_settings = {}

    async def load_cog(self, directory: str, file: str):
        if file.endswith('.py'):
            try:
                await self.load_extension(f'{directory}.{file[:-3]}')
                self.logger.info('Loaded extension %s.%s', directory, file[:-3])
            except commands.errors.NoEntryPointError:
                pass

    async def setup_hook(self):
        self.remove_command('help')
        self.add_check(self.globally_block_dms)

        ignore_items = ['__pycache__']
        for item in os.listdir('cogs'):
            if item in ignore_items:
                continue

            if os.path.isdir(f'cogs/{item}'):
                for file in os.listdir(f'cogs/{item}'):
                    await self.load_cog(f'cogs.{item}', file)
            else:
                await self.load_cog('cogs', item)

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.process_commands(message)

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.connected:
            for guild in self.guilds:
                await set_guild_invites(self, guild)

            self.logger.critical('logged in as %s | %s', self.user.name, self.user.id)
            self.connected = True

    async def globally_block_dms(self, ctx: commands.Context):
        return ctx.guild is not None
