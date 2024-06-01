import sys

from config.secrets import TOKEN
from ext.discord_bot import DiscordBot
from ext.logger import logger, LoggingHandler


bot = DiscordBot(logger)
logger_handler = LoggingHandler(sys.stdout, bot)
logger.addHandler(logger_handler)

if __name__ == '__main__':
    bot.run(TOKEN)
