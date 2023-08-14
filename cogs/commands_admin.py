import json

import discord
from discord.ext import commands

from ext.functions import set_guild_invites

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name='settings', description='Configure server logging settings - choose any or all of the parameters')
    @discord.app_commands.guild_only
    @discord.app_commands.default_permissions()
    @discord.app_commands.describe(log_type='The type of log to manage')
    @discord.app_commands.describe(enabled='Enable or disable this log type')
    @discord.app_commands.choices(log_type=[
        discord.app_commands.Choice(name='Audit Log', value='audit'),
        discord.app_commands.Choice(name='Ban Log', value='ban'),
        discord.app_commands.Choice(name='Delete Log', value='delete'),
        discord.app_commands.Choice(name='Edit Log', value='edit'),
        discord.app_commands.Choice(name='Join Log', value='join'),
        discord.app_commands.Choice(name='Rejoin Log', value='rejoin'),
        discord.app_commands.Choice(name='Kick Log', value='kick'),
        discord.app_commands.Choice(name='Onboarding Log', value='onboarding'),
        discord.app_commands.Choice(name='Moderator Delete', value='delete'),
        discord.app_commands.Choice(name='Moderator Nickname Manage Log', value='moderator_nick'),
        discord.app_commands.Choice(name='Moderator Role Manage Log', value='moderator_role'),
        discord.app_commands.Choice(name='Moderator Voice Disconnect', value='moderator_disconnect'),
        discord.app_commands.Choice(name='Moderator Voice Move', value='move'),
        discord.app_commands.Choice(name='Message Pin / Unpin', value='pin'),
        discord.app_commands.Choice(name='Nick Log', value='nick'),
        discord.app_commands.Choice(name='Onboarding Log', value='onboarding'),
        discord.app_commands.Choice(name='Part Log', value='part'),
        discord.app_commands.Choice(name='Pending Log', value='pending'),
        discord.app_commands.Choice(name='Role Log', value='role'),
        discord.app_commands.Choice(name='Timeout Log', value='timeout'),
        discord.app_commands.Choice(name='Username Log', value='username'),
        discord.app_commands.Choice(name='Voice Log', value='voice')
    ])
    @discord.app_commands.describe(channel='Text channel where the selected log message will be sent')
    @discord.app_commands.describe(label='Short label for the selected log message')
    @discord.app_commands.describe(message_format='Format for the selected log message')
    @discord.app_commands.choices(message_format=[
        discord.app_commands.Choice(name='Text', value='text'),
        discord.app_commands.Choice(name='Simple Embed', value='simple'),
        discord.app_commands.Choice(name='Extended Embed', value='extended')
    ])
    @discord.app_commands.describe(icon_url='URL for the selected log message icon')
    async def settings(
        self,
        interaction: discord.Interaction,
        log_type: str,
        enabled: bool,
        channel: discord.TextChannel = None,
        label: str = None,
        message_format: str = None,
        icon_url: str = None
    ):
        # url checker
        with open('config/guild_settings.json', 'r', encoding='utf-8') as file_pointer:
            guild_settings = json.load(file_pointer)

        if str(interaction.guild.id) in guild_settings:
            settings = []
            if enabled:
                guild_settings[str(interaction.guild.id)][log_type]['enabled'] = enabled
                settings.append(f'Enabled: {enabled}')
            if label:
                guild_settings[str(interaction.guild.id)][log_type]['label'] = label
                settings.append(f'Label: {label}')
            if channel:
                guild_settings[str(interaction.guild.id)][log_type]['channel_id'] = str(channel.id)
                settings.append(f'Log Channel: {channel.mention}')
            if message_format:
                guild_settings[str(interaction.guild.id)][log_type]['message_format'] = message_format
                settings.append(f'Message Format: {message_format}')
            if icon_url:
                guild_settings[str(interaction.guild.id)][log_type]['icon'] = icon_url
                settings.append(f'Icon URL: {icon_url}')

            with open('config/guild_settings.json', 'w', encoding='utf-8') as file_pointer:
                json.dump(guild_settings, file_pointer, indent=4)

            self.bot.guild_settings[interaction.guild.id] = guild_settings[str(interaction.guild.id)]
            await set_guild_invites(bot=self.bot, guild=interaction.guild)

            join_string = '\n > '
            await interaction.response.send_message(f'Updated **{log_type.capitalize()} Log** settings\n> {join_string.join(settings)}', ephemeral=True)

        else:
            await interaction.response.send_message('Logging for this guild is not setup')

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
