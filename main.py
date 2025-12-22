import discord

from discord.ext import commands

from utils import config, tools

token = config.token
cogs = ["cogs.commands.admin", "cogs.commands.configs", "cogs.commands.economy", "cogs.commands.fun", "cogs.commands.help",
        "cogs.commands.logging", "cogs.commands.misc", "cogs.commands.music", "cogs.commands.moderation",
        "cogs.commands.points", "cogs.commands.roles", "cogs.commands.tools", "cogs.commands.voice",
        "cogs.events.handler", "cogs.events.logger"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Flame(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = tools.get_prefix,
            intents = intents,
            strip_after_prefix = True,
            case_insensitive = True,
            help_command = None,
            status = discord.Status.online,
            activity = discord.Activity(
                type = discord.ActivityType.listening,
                name = "/help"))
        self.wiki = config.wiki
        self.server = config.server
        self.success = config.success
        self.fail = config.fail
        self.warning = config.warning
        self.working = config.working
        self.color = config.color
    
    async def setup_hook(self):
        for cog in cogs:
            await self.load_extension(cog)
            print(cog, "activated!")
        await self.tree.sync()
    
    async def on_ready(self):
        print(f"Logged in as: {self.user}")

bot = Flame()
bot.run(token)