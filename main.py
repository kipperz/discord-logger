import os
import sys

SECRETS_PATH = 'config/secrets.py'

if not os.path.exists(SECRETS_PATH):
    os.makedirs('config', exist_ok=True)
    with open(SECRETS_PATH, 'w', encoding='utf-8') as f:
        f.write("TOKEN = ''\nMONGO_URI = ''\n")

    print(f'Created "{SECRETS_PATH}". Please set the TOKEN and MONGO_UR variables')
    sys.exit(1)

from config.secrets import TOKEN
from ext.discord_bot import DiscordBot
from ext.logger import logger, LoggingHandler


bot = DiscordBot(logger)
logger_handler = LoggingHandler(sys.stdout, bot)
logger.addHandler(logger_handler)

if __name__ == '__main__':
    bot.run(TOKEN)
