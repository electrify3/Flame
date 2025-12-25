import time
import typing

import discord

from discord.ext import commands
from discord.ui import Button, View

from utils import tools

if typing.TYPE_CHECKING:
    from main import Bot

class Handler(commands.Cog):
    def __init__(self, bot: 'Bot'):
        self.bot: Bot = bot
    
    @commands.Cog.listener("on_message")
    async def manage_afk(self, message: discord.Message):
        if message.author.bot or message.channel == message.author.dm_channel: return
            
        if str(message.author.id) in tools.get_afk() and tools.get_afk()[str(message.author.id)]["message"]:
            if time.time() - tools.get_afk()[str(message.author.id)]["time"] > 10:
                tools.remove_afk(message.author)
                await message.reply(f"**Welcome back {message.author}, i changed your status to online!**", delete_after=5)
        
        for member in message.mentions:
            if member is message.author:
                continue
            if str(member.id) in tools.get_afk() and tools.get_afk()[str(member.id)]["message"]:
                msg = tools.get_afk()[str(member.id)]["message"]
                await message.reply(f"{member} is afk <t:{int(tools.get_afk()[str(member.id)]['time'])}:R>: {msg}", allowed_mentions=discord.AllowedMentions.none())
    
    
    @commands.Cog.listener("on_message")
    async def return_prefix(self, message: discord.Message):
        invite = Button(label="Invite Me", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=1513962695871&scope=bot%20applications.commands")
        server = Button(label="Support server", url=self.bot.server)
        view = View()
        view.add_item(invite)
        view.add_item(server)
        if message.author.bot:
            return
        if message.content.startswith(self.bot.user.mention) :
            prefix = await self.bot.get_prefix(message)
            if prefix:
                embed = discord.Embed(title = f'› My prefix is `{prefix}`\n› To get started type `{prefix}help`', color =self.bot.color)
            else:
                embed = discord.Embed(title = f'› No prefix is enabled in this server!\n› To get started type `help`', color=self.bot.color)
            await message.reply(embed=embed, view=view, mention_author=False)
    
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
            return

        embed = discord.Embed(colour=self.bot.color)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)


        if isinstance(error, commands.MissingPermissions):
            embed.description = f"{self.bot.fail} | You don't have enough permissions to run this command!"
            await ctx.send(embed=embed, ephemeral=True)

        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = f"{self.bot.fail} | I don't have enough permissions to execute this command!"
            await ctx.send(embed=embed, ephemeral=True)

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f'{self.bot.warning} | You are on cooldown. Try again after {int(error.retry_after)} seconds!'
            await ctx.send(embed=embed, ephemeral=True)

        else:
            view = View()
            view.add_item(Button(label="Support server", url=self.bot.server))

            embed.description = f'{self.bot.fail} | {error}!'
            await ctx.send(embed=embed, view=view, ephemeral=True)

async def setup(bot: 'Bot'):
    await bot.add_cog(Handler(bot))