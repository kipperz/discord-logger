import asyncio
import json
import logging
import os
import sys

import discord
from discord.ext import commands

import config


logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = config.settings.COMMAND_PREFIX,
            intents = discord.Intents.all(),
            log_hander = logger
        )
        self.logger = logger
        self.synced = False # still needed?
        self.guild_settings = {}

    async def load_cog(self, directory, file):
        if file.endswith('.py'):
            try:
                await bot.load_extension(f'{directory}.{file[:-3]}')
                self.logger.info('Loaded extension %s.%s', directory, file[:-3])
            except discord.ext.commands.errors.NoEntryPointError:
                pass

    async def setup_hook(self):
        ignore_items = ['__pycache__']
        for item in os.listdir('cogs'):
            if item in ignore_items:
                continue

            if os.path.isdir(f'cogs/{item}'):
                for file in os.listdir(f'cogs/{item}'):
                    await self.load_cog(f'cogs.{item}', file)
            else:
                await self.load_cog('cogs', item)

    async def on_ready(self):
        await self.wait_until_ready()

        with open('config/guild_settings.json', 'r', encoding='utf-8') as json_file:
            settings = json.load(json_file)

        for guild in self.guilds:
            if str(guild.id) in settings:
                self.guild_settings[guild.id] = settings[str(guild.id)]

                try:
                    self.guild_settings[guild.id]['invites'] = await guild.invites()
                except discord.Forbidden:
                    self.logger.warning('not tracking invites for guild %s %s - Missing Permissions', guild, guild.id)

            else:
                self.logger.warning('logging disabled for guild %s %s - No Settings', guild, guild.id)

        self.logger.critical('logged in as %s | %s', self.user.name, self.user.id)

bot = DiscordBot()
bot.remove_command('help')

class LoggingHandler(logging.Handler):
    def __init__(self, stdout, discord_bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stdout = stdout
        self.bot = discord_bot

    async def send_log(self, record):
        log_entry = self.format(record)
        if 'We are being rate limited' not in str(record):
            if config.settings.DEV_CHANNEL:
                channel = self.bot.get_channel(config.settings.DEV_CHANNEL)
                if channel is None:
                    pass
                else:
                    await channel.send(f'```prolog\n{log_entry[:1800]}```')

    def emit(self, record):
        asyncio.ensure_future(self.send_log(record))
        self.stdout.write(self.format(record) + '\n')

logger_handler = LoggingHandler(sys.stdout, bot)
logger_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(logger_handler)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

if __name__ == '__main__':
    bot.run(config.secrets.TOKEN)
