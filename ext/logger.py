import asyncio
import logging

import config


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

class LoggingHandler(logging.Handler):
    def __init__(self, stdout, discord_bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLevel(logging.WARNING)
        self.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
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
