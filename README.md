Flame
=====

**Flame** is a versatile, self-hosted Discord bot built for server management and community engagement. It supports both prefix (`??`) and slash (`/`) commands, with features spanning moderation, logging, role management, economy (points) system, music playback, utilities, and fun commands. Key highlights include an **interactive music player powered by Lavalink** (for high-quality audio streaming), a persistent SQLite-backed database for settings and leaderboards, and a rich suite of automated tools (like message embedder, polls, and even a “sniping” deleted-message fetcher). Flame uses intuitive status emojis for success/warning/failure and is designed to be user-friendly and extensible.

Features
--------

*   **Moderation**: Kick, ban, mute, auto-moderation filters, and more – with audit logging.
*   **Logging**: Tracks joins, leaves, deleted messages, infractions, etc., storing them in a database for later review.
*   **Role Management**: Bulk-assign or remove roles to/from one or many members at once.
*   **Economy/Points**: Manage user points (XP/currency) and display leaderboards with pagination.
*   **Music Playback**: Stream music from YouTube and other sources using a Lavalink server. Provides queue, skip, pause, loop, and interactive buttons in Discord for control.
*   **Utilities**: Miscellaneous commands like `embed` (send a custom embed), `nuke` (bulk-delete with confirmation), `snipe` (retrieve last deleted message), `steal` (copy emojis), etc.
*   **Fun Commands**: Image searches, jokes, or trivia (e.g. web requests, game commands) for entertainment.
*   **Custom Configurations**: Server-specific settings (prefix, toggles, etc.) stored in an SQLite database.

Flame’s **slash command support** means you can type commands with `/` and see autocomplete, alongside its traditional prefix (`??`) commands. This ensures broad compatibility across servers.

Setup & Requirements
--------------------

Flame runs on **Python 3.8+**. It also requires a separate **Java-based Lavalink server** for music. Before running Flame, ensure you have the following installed and configured:

*   **Python 3.8 or newer**: Install from python.org and use `pip` to install dependencies.
*   **Dependencies**: From the repository root, run:
    ```bash
    pip install -r requirements.txt
    ```
    This installs libraries like `discord.py`, `lavalink`, `aiohttp`, `yt-dlp`, etc.
*   **Discord Bot Application**: Create a bot in the Discord Developer Portal and get its **Token**. In your application’s _Bot_ settings, **enable the Message Content Intent** (and also _Server Members Intent_ if using member-based commands).
*   **.env Configuration**: Copy `.env.example` to `.env` and set the following environment variables:
    *   `TOKEN`: your Discord bot token.
    *   `TENOR`: (optional) a Tenor API key for GIF commands.
*   **Lavalink Server**: You'll need to setup a [Lavalink server](https://github.com/lavalink-devs/Lavalink), Flame will connect to this for music streaming. You may need to do some tweaks in `cogs/music.py` too.
*   **FFmpeg**: Install FFmpeg on your system PATH. This is required if youre using ffmpeg music module in `extras/`.
*   **Invite the Bot**: Use the OAuth2 URL Generator in the Developer Portal (scopes `bot` and `applications.commands`) and give it the needed permissions (e.g. Manage Messages, Manage Roles, Send Messages, Connect/Speak for voice, etc.). The bot can only be invited to servers where you have the **Manage Server** permission. See Discord’s documentation for generating an invite link.

Running the Bot
---------------

1.  **Database Files**: On first run, Flame will auto-create SQLite DB files in `data/database/` for configs, logs, and points. No manual setup needed.
2.  **Launch**: Run the main script:
    ```bash
    python main.py
    ```
    The bot will load all cogs (modules) and become online. In console it will print messages like `cogs.commands.admin activated!`.
3.  **Initial Commands**: Once running, the bot responds to the default prefix `??`. Use `??help` or `/help` to see available commands. You can also ping the bot (like `@Flame`) to have it display the current prefix for your server.

Usage Highlights
----------------

*   **Prefix & Slash**: Flame’s commands can be used as either traditional prefix commands or as slash commands. For example, `??ban @user reason` or `/ban @user reason` (as a slash command). Slash commands will only work after the bot’s commands have been synced (this happens on start).
*   **Configuration Commands**: The bot has admin-only groups (e.g. `admin`, `configs`) for changing settings like prefix or toggling features (e.g. disabling music or logging). These commands are restricted to the bot owner/admins or server administrators.
*   **Role Command Example**: The `??role` group can add or remove a role for multiple users at once. For example, `??role add @Alice @Bob Member` assigns the _Member_ role to Alice and Bob. This makes bulk role management easy without having to click in the Discord UI.
*   **Music Commands**: Use `??play <query>` to search/play music. The bot will display an embed showing the current track and add buttons for _pause_, _skip_, _stop_, _loop_, etc. You can also manage the queue (view next tracks) with buttons that page through results. Because it uses Lavalink, audio streaming is efficient and high-quality. (You must have the Lavalink server running for music to work.)
*   **Points/Leaderboard**: Administrators can award or set points for members (e.g. `??points add @User 100`). Any member can view the server’s points leaderboard with pagination. This can be used for gamification or reward systems.
*   **Logging**: You can configure a channel for mod logs. When enabled, events like member joins/leaves or message deletions are logged into the database and can be viewed with commands (or automatically posted to a channel if coded).
*   **Utilities**:
    *   `??embed` lets an admin send a custom embed in any channel.
    *   `??nuke` (with confirmation) bulk-deletes messages in a channel (for quick moderation cleanup).
    *   `??snipe` retrieves the last deleted message in a channel.
    *   `??steal` can copy custom emojis given an emoji or image URL.
        These tools streamline many repetitive tasks in servers.
*   **Fun Commands**: There are likely commands under `fun` (e.g. image search, random memes, or facts). Check `/help` for specifics. These provide light-hearted entertainment and enhance engagement.

Support and Links
-----------------

*   Consult the bot’s **built in help command** for command details and examples.
*   Keep your bot updated: pull changes from this repo and restart.
*   The code is **open-source** under the Apache 2.0 license (see `LICENSE` file). You can modify and adapt it to your needs.

Flame is designed to be a full-featured yet easy-to-run bot. By following the above setup and using the built-in commands, you can manage your Discord community effectively. Enjoy the blend of utility and fun that Flame brings to your server!