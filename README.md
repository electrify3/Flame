# Flame - Multipurpose Discord Bot

Introducing Flame, a versatile Discord bot that brings multiple moderation and action features to your server. With Flame at your command, managing your server becomes easy and fast, thanks to its user-friendly commands and intuitive design.

## Default Prefix and Customization

By default, Flame's command prefix is `?`, allowing users to easily trigger its features. However, if you prefer a different prefix or even `no prefix` at all, Flame offers the flexibility to customize it to suit your server's needs.

## Powerful Features

Flame excels at making complex tasks simple. Take, for instance, the role management feature. Adding a role to multiple members simultaneously is effortless with Flame. By using the command `?role @user1/id @user2/id... role name/id`, you can assign roles to several members at once. Flame takes care of case sensitivity and font variations, ensuring a seamless role assignment process.

Moderation commands are another highlight of Flame. Whether you need to kick, ban, or manage user permissions, Flame provides efficient moderation tools to keep your server in check. You can swiftly handle user actions with just a few commands, making moderation hassle-free.

Additionally, Flame offers a variety of miscellaneous commands that enhance your server's experience. Enjoy engaging activities like truth or dare, or express emotions using special emotes such as hugs and kisses. Flame's diverse range of features ensures that there's something for everyone in your community.

## The Points System

Flame introduces a points system designed with tournaments in mind. With this system, users can log their own points without any intervention from staff members. This self-service approach allows for easy participation and tracking during tournaments or competitive events on your server. The points system provides a seamless and transparent way for users to keep track of their progress.

## Command Categories

- **Miscellaneous**: Provides various commands and functionalities.
- **Voice**: Handles voice-related commands and operations.
- **Fun**: Offers interactive and entertaining commands.
- **Moderation**: Manages moderation commands and features for server administration.
- **Points**: Implements a points system for tournaments or competitive events.
- **Roles**: Handles role-related commands and operations.
- **Configs**: Manages bot configuration settings.

# Getting Started
**Set the following env variables first**
 - `Token` = discord bot api key/token
 - `OpenAI` = openai key (leave this as none or empty string if not available)
 - `TenorKey` = tenor api key (for gifs)

# Customisation
**To customise bot apperance you need to go through** `Flame/utils/config.py`
- **You can change embed colour, primary emojis, links, prefix and bot admins**
Note: some emojis you need to change manually (eg. in file help.py)

# Do you like replit?
**here is direct repl link of this bot: [Flame](https://replit.com/@electrify3/Flame)**
