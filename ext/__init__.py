import discord


def get_username(user_object: discord.abc.User, escape_markdown: bool = False):
    if isinstance(user_object, discord.Member):
        username = str(user_object._user) #pylint: disable=protected-access
    else:
        username = str(user_object)

    if escape_markdown:
        username = discord.utils.escape_markdown(username)

    return username
