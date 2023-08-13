from pymongo import MongoClient

from config.secrets import MONGO_URI

COMMAND_PREFIX = '%'

DEV_CHANNEL = 1138601380374904964

mongo = MongoClient(MONGO_URI)
log_database = mongo['logs']

# # Channel Definitions
# AUDIT_LOG = 1139070096636121098
# ERROR_LOG = 1138601380374904964
# GUILD_UPDATES = 1138601380374904964
# JOIN_PART = 1139327710343204984
# MEMBER_ACTIONS = 1138601380374904964
# MESSAGE_LOG = 1138601380374904964
# MODERATION_ACTIONS = 1139080828098457650


# class LogSettings:
#     MESSAGE_FORMAT_TYPES = ['text', 'simple', 'extended']

#     def __init__(
#         self,
#         label: str = None,
#         channel_id: int = None,
#         message_format: str = 'simple',
#         icon: str = None
#     ):
#         if label is not None:
#             if not isinstance(label, str):
#                 raise ValueError('label must be a string')

#         if channel_id is not None:
#             if not isinstance(channel_id, int):
#                 raise ValueError('channel_id must be an integer')

#         if not isinstance(message_format, str):
#             raise ValueError('message_format must be a string')

#         if message_format not in self.MESSAGE_FORMAT_TYPES:
#             raise ValueError(f'message_format must be one of {", ".join(self.MESSAGE_FORMAT_TYPES)}')

#         if icon is not None:
#             if not isinstance(icon, str):
#                 raise ValueError('icon must be a URL string')

#         self.label = label
#         self.id = channel_id #pylint: disable=invalid-name
#         self.message_format = message_format
#         self.icon = icon


# JOIN_LOG = LogSettings(label='joined', channel_id=JOIN_PART, icon='https://cdn.discordapp.com/attachments/1139327297955037224/1139327340871164065/arrow_join.png')
# REJOIN_LOG = LogSettings(label='rejoin', channel_id=JOIN_PART, icon='https://cdn.discordapp.com/attachments/1139327297955037224/1139327340871164065/arrow_join.png')
# PART_LOG = LogSettings(label='parted', channel_id=JOIN_PART, icon='https://cdn.discordapp.com/attachments/1139327297955037224/1139327341148000296/arrow_leave.png')
# AUDIT_LOG = LogSettings(label='audit log', channel_id=AUDIT_LOG)
# BAN_LOG = LogSettings(label='banned', channel_id=MODERATION_ACTIONS)
# DELETE_LOG = LogSettings(channel_id=MESSAGE_LOG)
# EDIT_LOG = LogSettings(channel_id=MESSAGE_LOG)
# KICK_LOG = LogSettings(label='kick', channel_id=MODERATION_ACTIONS)
# NICK_LOG = LogSettings(label='nickname', channel_id=MEMBER_ACTIONS) # could be moderator actions
# ONBOARDING_LOG = LogSettings(label='onboarding', channel_id=MEMBER_ACTIONS)
# PENDING_LOG = LogSettings(label='pending', channel_id=MEMBER_ACTIONS)
# ROLE_LOG = LogSettings(label='role', channel_id=MODERATION_ACTIONS)
# TIMEOUT_LOG = LogSettings(label='timeout', channel_id=MODERATION_ACTIONS)
# USERNAME_LOG = LogSettings(label='username', channel_id=MEMBER_ACTIONS)
# VOICE_LOG = LogSettings(label='voice', channel_id=MEMBER_ACTIONS) # could be moderator
