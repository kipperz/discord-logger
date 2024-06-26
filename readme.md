
# Discord Logger

Discord Logger is an open-source bot designed to meticulously log messages and events in Discord without the bloat of an all-in-one bot. Written in python using the discord.py library, this bot is easy to setup and can log multiple servers. Coded for use with or without a mongodb database.

📝 **About**:
Discord Logger is in early-development and is brought to you by kipperz, streamer [twitch.tv/kipperzGG](https://twitch.tv/kipperzGG) and owner/developer of [discord.gg/kipperz](https://discord.gg/kipperz).

## Beta Release
- **Version 0.9.5**: The secrets.py file is now created on first run and is included in .gitignore. Please remember to keep your token secure. Fixed a check that was excluding message reply logging.
- **Version 0.9.4**: Created separate files for the DiscordBot and LoggingHandler classes. Updated DiscordBot class setup_hook and on_ready methods. Fixed some typing errors.
- **Version 0.9.3**: Discord Logger is not yet ready for full deployment. Ahead of our 1.0 release, we're improving message formats and testing thoroughly. To assist in testing, contact kipperz on Discord.

## Features

- **Moderator Action Logging**: Keep track of all actions taken by server moderators, providing accountability and traceability.

- **Audit Log Backup**: Don't lose your server's audit logs. Discord retains your audit log for just 90 days, but with Discord Logger, you can back them up in a designated text channel and/or a database.

- **Member Tracking**:
  - **Join/Part Logging**: Monitor when members join or leave the server.
  - **Invite Tracker**: Log the invite used with the member join message.
  - **Action Logging**: Record username and nickname changes to keep track of member identities.

- **Message Logging**:
  - **Database Logging**: Preserve all messages in a dedicated database, ensuring you never lose important information.
  - **Edit & Delete Tracking**: Capture edits and deletions to maintain the integrity of server communications. Leverage the database when message data is not cached.

- **Voice Chat Logs**: Gain insights into voice chat usage, understanding patterns, durations, and participation.

## Future Features

- **Improved Audit Log Messages**: Send the audit log to a channel with full details

- **Preview Log Formats**: In /setup, preview text, simple, and extended embeds for each log type

- **Attachment Logging**

- **Avatar Logging**

- **Attachment Logging**


## Self-Hosting

Currently, your option for using Discord Logger is to self-host. The bot is designed with multi-server support, making it versatile for various community sizes.

### Installation & Setup

1. Clone and install dependencies
   ```
   git clone https://github.com/kipperz/discord-logger.git
   ```
   ```
   cd discord-logger
   ```
   ```
   pip install -r requirements.txt
   ```

2. Configure settings.py & secrets.py in the config dir

3. Launch the bot
   ```
   python main.py
   ```

4. Use the `sync` command, then `/setup`

## Support & Contribution

For support, feature requests, or contributions, please open an issue on this repository. If you appreciate the work and wish to support the development, consider checking out [kipperz on Twitch](https://twitch.tv/kipperzGG) or joining the official [Discord server](https://discord.gg/kipperz).
