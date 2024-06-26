from typing import Union

import discord
from discord.ext import commands
from pymongo import DESCENDING, MongoClient

from config.secrets import MONGO_URI
from ext.audit_log import recursive_object_to_dict

if MONGO_URI:
    log_database = MongoClient(MONGO_URI)
else:
    log_database = None

def database_insert_message(message: discord.Message):
    doc = {
        'message_id': str(message.id),
        'guild_id': str(message.guild.id),
        'channel_id': str(message.channel.id),
        'author': str(message.author),
        'author_id': str(message.author.id),
        'created_at': message.created_at,
        'content': message.content,
        'edited_at': message.edited_at,
        'deleted': False,
    }

    result = log_database[str(message.guild.id)][str(message.channel.id)].insert_one(doc)
    if result.inserted_id is not None and result.acknowledged is True:
        pass
    else:
        pass # error logger

def database_insert_audit_log_entry(entry: discord.AuditLogEntry):
    result = log_database[str(entry.guild.id)].audit_log.insert_one(recursive_object_to_dict(entry))
    if result.inserted_id is not None and result.acknowledged is True:
        pass
    else:
        print('new log not inserted')

def database_delete_message(message: Union[discord.Message, classmethod]): # Marks message as deleted in the message docs
    result = log_database[str(message.guild.id)][str(message.channel.id)].update_many({'message_id': str(message.id)}, {'$set': {'deleted': True}})
    if result is None:
        pass # error logger

async def database_get_last_message(bot: commands.Bot, guild_id: int, channel_id: int, message_id: int):
    message_doc = log_database[str(guild_id)][str(channel_id)].find_one({'message_id': str(message_id)}, sort=[('edited_at', DESCENDING)])
    if message_doc is None:
        message_doc = {}
        class message_author: #pylint: disable=invalid-name
            bot = False
    else:
        message_author = await bot.fetch_user(message_doc['author_id'])

    guild_object = bot.get_guild(guild_id)
    class Message:
        id = message_id
        author = message_author
        guild = guild_object
        channel = guild.get_channel(channel_id)
        created_at = message_doc.get('created_at', None)
        edited_at = message_doc.get('edited_at', None)
        content = message_doc.get('content', '')
        type = discord.MessageType.default

    return Message
