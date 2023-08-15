
# Discord Logger

Discord Logger is an open-source bot designed to meticulously track and log server events in Discord. Written in python using the discord.py library, this bot is easy to setup and can log multiple servers. Coded for use with or without a mongodb database.

📝 **About**:
Discord Logger is in early-development and is brought to you by kipperz, streamer [twitch.tv/kipperzGG](https://twitch.tv/kipperzGG) and owner/developer of [discord.gg/kipperz](https://discord.gg/kipperz).

## Beta Release
- **Version 0.9.2**: Discord Logger is not yet ready for full deployment. Ahead of our 1.0 release, we're adding a /setup command, improving message formats, and testing thoroughly. To assist in testing, contact kipperz on Discord.

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

## Self-Hosting

Currently, your option for using Discord Logger is to self-host. The bot is designed with multi-server support, making it versatile for various community sizes.

### Installation & Setup

1. Clone this repository:
   ```
   git clone https://github.com/kipperz/discord-logger.git
   ```

2. Navigate to the repository directory and install required dependencies.

3. Modify config/settings.py

4. Modify config/guild_settings.json

5. Launch the bot:
   ```
   python main.py
   ```

## Support & Contribution

For support, feature requests, or contributions, please open an issue on this repository. If you appreciate the work and wish to support the development, consider checking out [kipperz on Twitch](https://twitch.tv/kipperzGG) or joining the official [Discord server](https://discord.gg/kipperz).
