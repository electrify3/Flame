import time

import discord

from discord.ext import commands
from discord.ui import Button, View

from utils import tools

class Handler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener("on_message")
    async def manage_afk(self, message):
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
    async def return_prefix(self, message):
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
    async def on_command_error(self, ctx, error):
        server = Button(label="Support server", url=self.bot.server)
        view = View()
        view.add_item(server)
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.message.reply(f"{self.bot.fail} | You don't have enough permissions to run this command!", view=view, mention_author=False)
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.message.reply(f"{self.bot.fail} | I don't have enough permissions to execute this command!", view=view, mention_author=False)
            return
        em = discord.Embed(title="Error!", description=error, color=discord.Colour.red())
        await ctx.send(embed=em, view=view, mention_author=False)

async def setup(bot):
    await bot.add_cog(Handler(bot))