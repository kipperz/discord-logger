import copy

import discord
from discord.ext import commands

from ext import functions


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    log_settings = {
        '⚙ View settings': 'view settings',
        '➡ Select a category for bulk settings, or type a category to list specific logs types': '',
        'CATEGORY:\u2002Audit Log': 'audit',
        'CATEGORY:\u2002Join Part': 'join_part',
        'CATEGORY:\u2002Messages': 'message_log',
        'CATEGORY:\u2002Member': 'member_actions',
        'CATEGORY:\u2002Moderator': 'moderator_actions',
        'CATEGORY:\u2002Voice': 'voice',
        'CATEGORY:\u2002Join Part — join log': 'join',
        'CATEGORY:\u2002Join Part — rejoin log': 'rejoin',
        'CATEGORY:\u2002Join Part — part log': 'part',
        'CATEGORY:\u2002Messages — delete log': 'delete',
        'CATEGORY:\u2002Messages — edit log': 'edit',
        'CATEGORY:\u2002Member — nickname log': 'nick',
        'CATEGORY:\u2002Member — onboarding log': 'onboarding',
        'CATEGORY:\u2002Member — pending log': 'pending',
        'CATEGORY:\u2002Member — role log': 'role',
        'CATEGORY:\u2002Member — username log': 'username',
        'CATEGORY:\u2002Moderator — ban log': 'moderator_ban',
        'CATEGORY:\u2002Moderator — deafen log': 'moderator_deafen',
        'CATEGORY:\u2002Moderator — delete log': 'moderator_delete',
        'CATEGORY:\u2002Moderator — disconnect log': 'moderator_disconnect',
        'CATEGORY:\u2002Moderator — kick log': 'moderator_kick',
        'CATEGORY:\u2002Moderator — move log': 'moderator_move',
        'CATEGORY:\u2002Moderator — mute log': 'moderator_mute',
        'CATEGORY:\u2002Moderator — nick log': 'moderator_nick',
        'CATEGORY:\u2002Moderator — pin log': 'moderator_pin',
        'CATEGORY:\u2002Moderator — role log': 'moderator_role',
        'CATEGORY:\u2002Moderator — timeout log': 'moderator_timeout'
    }

    @discord.app_commands.command(name='setup', description='Customize, confirm, and preview server logging')
    @discord.app_commands.guild_only
    @discord.app_commands.default_permissions()
    @discord.app_commands.describe(log_type='Log category or log type to configure')
    @discord.app_commands.describe(channel='Text channel for log messages')
    @discord.app_commands.describe(label='Short label for log messages')
    @discord.app_commands.describe(message_format='Format for log messages')
    @discord.app_commands.choices(message_format=[
        discord.app_commands.Choice(name='Text', value='text'),
        discord.app_commands.Choice(name='Simple Embed', value='simple'),
        discord.app_commands.Choice(name='Extended Embed', value='extended')
    ])
    @discord.app_commands.describe(icon_url='URL for icons in certain log messages')
    @discord.app_commands.describe(disabled='Enable or disable logging')
    @discord.app_commands.describe(ignore_channel='Add a text channel to the message logging ignore list')
    async def setup(
        self,
        interaction: discord.Interaction,
        log_type: str,
        channel: discord.TextChannel = None,
        label: str = None,
        message_format: str = None,
        icon_url: str = None,
        disabled: bool = False,
        ignore_channel: discord.TextChannel = None
    ):
        if log_type == '' or log_type not in self.log_settings.values():
            await interaction.response.send_message('Error: Please select a valid category or log type', ephemeral=True)
            return

        if icon_url == 0:
            await interaction.response.send_message('Error: Invalid icon URL', ephemeral=True)
            return

        if ignore_channel and log_type not in ['message_log', 'delete', 'edit']:
            await interaction.response.send_message('Error: Ignore Channel can only be enabled for Message Logs', ephemeral=True)
            return

        guild_settings = functions.get_guild_settings()

        if str(interaction.guild.id) not in guild_settings:
            guild_settings[str(interaction.guild.id)] = copy.deepcopy(guild_settings['template'])

        if log_type == 'view settings':
            category_label = 'AUDIT LOG'

        else:
            if log_type in functions.guild_settings_categories: # Category Settings
                if not disabled and not channel:
                    await interaction.response.send_message('Error: A text channel must be provided when a category is selected', ephemeral=True)
                    return

                if 1 == 2: # UPDATE check for channel permissions
                    await interaction.response.send_message(f'Error: missing permissions in {channel.mention}', ephemeral=True)
                    return

                for log_type_setting, settings in guild_settings[str(interaction.guild.id)].items():
                    if settings['category'] == log_type:
                        guild_settings = self.configure_log_type(guild_settings, interaction.guild.id, log_type_setting, channel, disabled, icon_url, label, message_format, ignore_channel.id if ignore_channel else None)

                category_label = self.create_category_label(log_type)

            else: # Individual Log Settings
                stored_channel_id = guild_settings[str(interaction.guild.id)][log_type]['channel_id']
                if not disabled and not channel and not stored_channel_id:
                    await interaction.response.send_message('Error: A text channel must be provided if a setting is enabled', ephemeral=True)
                    return

                if 1 == 2: # UPDATE check for channel permissions
                    if not channel:
                        channel = self.bot.get_channel(int(stored_channel_id))
                    await interaction.response.send_message(f'Error: missing permissions in {channel.mention}', ephemeral=True)
                    return

                guild_settings = self.configure_log_type(guild_settings, interaction.guild.id, log_type, channel, disabled, icon_url, label, message_format, ignore_channel.id if ignore_channel else None)

                category_label = self.create_category_label(guild_settings[str(interaction.guild.id)][log_type]['category'])

        self.bot.guild_settings[interaction.guild.id] = guild_settings[str(interaction.guild.id)]
        functions.write_guild_settings(guild_settings)
        await functions.set_guild_invites(bot=self.bot, guild=interaction.guild)

        embeds = self.guild_settings_to_embeds(guild_settings=guild_settings[str(interaction.guild.id)])
        await interaction.response.send_message(embed=discord.Embed.from_dict(embeds[category_label]), ephemeral=True, view=self.GuildSettings(embeds, category_label))
        # UPDATE send view with select to preview messages

    @setup.autocomplete('log_type')
    async def log_type_autocomplete(self, interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
        if current == '':
            start_index, end_index = 0, 8
        else:
            start_index, end_index = 1, 24

        return [
            discord.app_commands.Choice(name=log_type, value=self.log_settings[log_type])
            for log_type in list(self.log_settings.keys())[start_index:] if current.lower() in log_type.lower()
        ][:end_index]

    def configure_log_type(self, guild_settings, guild_id, log_type, channel, disabled, icon_url, label, message_format, ignore_channel):
        if channel:
            guild_settings[str(guild_id)][log_type]['channel_id'] = str(channel.id)
        guild_settings[str(guild_id)][log_type]['disabled'] = disabled
        if icon_url:
            guild_settings[str(guild_id)][log_type]['icon'] = icon_url
        if label:
            guild_settings[str(guild_id)][log_type]['label'] = label
        if message_format:
            guild_settings[str(guild_id)][log_type]['message_format'] = message_format
        if ignore_channel:
            guild_settings[str(guild_id)][log_type]['ignore_channels'].append(ignore_channel)
        return guild_settings

    def guild_settings_to_embeds(self, guild_settings):
        embeds = {}
        for category in functions.guild_settings_categories:
            category_settings = {k: v for k, v in guild_settings.items() if v["category"] == category}

            description = []
            for category_setting, items in category_settings.items():
                if items['disabled']:
                    description.append(f'`{category_setting} log` **disabled**\n\n')
                else:
                    description.append(f'`{category_setting} log`\n> **Channel**: <#{items["channel_id"]}>\n> **Label**: {items["label"]}\n> **Message Format**: {items["message_format"]}\n> {"Icon" if items["icon_url"] else "No Icon"}')
                    if items["ignore_channels"]:
                        description.append('\n> **Ignored Channels**: ')
                        for channel_id in items["ignore_channels"]:
                            description.append(f'<#{channel_id}> ')
                    description.append('\n\n')

            category_label = self.create_category_label(category)
            embed = functions.embeds.create_embed(author=category_label, description=description)
            embeds[category_label] = embed.to_dict()

        return embeds

    def create_category_label(self, category):
        return category.replace('_',' ').upper()

    class GuildSettings(discord.ui.View):
        def __init__(self, embeds: dict, category_label):
            super().__init__(timeout=None)
            self.embeds = embeds

            buttons = {
                AdminCommands.AuditLog: 'AUDIT LOG',
                AdminCommands.JoinPart: 'JOIN PART',
                AdminCommands.MemberActions: 'MEMBER ACTIONS',
                AdminCommands.MessageLog: 'MESSAGE LOG',
                AdminCommands.ModeratorActions: 'MODERATOR ACTIONS',
                AdminCommands.Voice: 'VOICE'
            }

            for button, category in buttons.items():
                if category == category_label:
                    self.add_item(button(disabled=True, embeds=embeds))
                else:
                    self.add_item(button(disabled=False, embeds=embeds))

    class AuditLog(discord.ui.Button):
        def __init__(self, disabled, embeds):
            self.embeds = embeds
            super().__init__(label='AUDIT LOG', style=discord.ButtonStyle.blurple, disabled=disabled, custom_id='guild_settings_audit_log', row=0)

        async def callback(self, interaction: discord.Interaction):
            functions.pagination(self.view, self)
            await interaction.response.edit_message(embed=discord.Embed.from_dict(self.embeds[self.label]), view=self.view)

    class JoinPart(discord.ui.Button):
        def __init__(self, disabled, embeds):
            self.embeds = embeds
            super().__init__(label='JOIN PART', style=discord.ButtonStyle.blurple, disabled=disabled, custom_id='guild_settings_join_part', row=0)

        async def callback(self, interaction: discord.Interaction):
            functions.pagination(self.view, self)
            await interaction.response.edit_message(embed=discord.Embed.from_dict(self.embeds[self.label]), view=self.view)

    class MemberActions(discord.ui.Button):
        def __init__(self, disabled, embeds):
            self.embeds = embeds
            super().__init__(label='MEMBER ACTIONS', style=discord.ButtonStyle.blurple, disabled=disabled, custom_id='guild_settings_member_actions', row=0)

        async def callback(self, interaction: discord.Interaction):
            functions.pagination(self.view, self)
            await interaction.response.edit_message(embed=discord.Embed.from_dict(self.embeds[self.label]), view=self.view)

    class MessageLog(discord.ui.Button):
        def __init__(self, disabled, embeds):
            self.embeds = embeds
            super().__init__(label='MESSAGE LOG', style=discord.ButtonStyle.blurple, disabled=disabled, custom_id='guild_settings_message_log', row=1)

        async def callback(self, interaction: discord.Interaction):
            functions.pagination(self.view, self)
            await interaction.response.edit_message(embed=discord.Embed.from_dict(self.embeds[self.label]), view=self.view)

    class ModeratorActions(discord.ui.Button):
        def __init__(self, disabled, embeds):
            self.embeds = embeds
            super().__init__(label='MODERATOR ACTIONS', style=discord.ButtonStyle.blurple, disabled=disabled, custom_id='guild_settings_moderator_actions', row=1)

        async def callback(self, interaction: discord.Interaction):
            functions.pagination(self.view, self)
            await interaction.response.edit_message(embed=discord.Embed.from_dict(self.embeds[self.label]), view=self.view)

    class Voice(discord.ui.Button):
        def __init__(self, disabled, embeds):
            self.embeds = embeds
            super().__init__(label='VOICE', style=discord.ButtonStyle.blurple, disabled=disabled, custom_id='guild_settings_voice', row=1)

        async def callback(self, interaction: discord.Interaction):
            functions.pagination(self.view, self)
            await interaction.response.edit_message(embed=discord.Embed.from_dict(self.embeds[self.label]), view=self.view)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
