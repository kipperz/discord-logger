from pymongo import MongoClient

from config.secrets import MONGO_URI

COMMAND_PREFIX = '%'

DEV_CHANNEL = 1138601380374904964

mongo = MongoClient(MONGO_URI)
log_database = mongo['logs']
