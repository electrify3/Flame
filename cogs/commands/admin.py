import discord
import sqlite3
from utils import config
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.emoji = "<:Eadmin:1127307669301121144>"
    
    
    async def cog_check(self, ctx):
        if ctx.author.id in config.admins:
            return True
        else:
            raise "You are not a admin of this bot."
    
    
    @commands.group(name="admin", description="this category commands can only be executed by bot admins.", invoke_without_command=True)
    async def admin(self, ctx):
        admins = [await self.client.fetch_user(admin) for admin in config.admins]
        description = "\n".join(f"{a.mention} [{a}]" for a in admins)
        em = discord.Embed(title="Admins", description=description, color=discord.Colour.blurple())
        await ctx.send(embed=em)
    
    
    @admin.command(name="bbg")
    async def bbg(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = "https://c.tenor.com/lEKBEbwZ7FAAAAAC/bbg-bbg-slap.gif"
        em = discord.Embed(color=self.client.color)
        em.set_author(name=f"{ctx.author.name} ne {user.name} ka suwar bhar diya", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    
    @admin.command()
    async def say(self, ctx,*, message=None):
        await ctx.message.delete()
        if message is None :
            reply = await ctx.send('No arguments provided!')
            await reply.delete(delay=5)
            return
        await ctx.send(f'{message}')
    
    @admin.command()
    async def reply(self, ctx, message : discord.Message,*, content):
        await ctx.message.delete()
        await message.reply(content) 
    
    
    @admin.command()
    async def guild(self, ctx, guild: discord.Guild):
        if guild.icon:
            em = discord.Embed(description=f"[Server icon]({guild.icon.url})", color = ctx.author.color)
            em.set_author(name=guild, icon_url=guild.icon.url) 
            em.set_thumbnail(url=guild.icon.url)
        else:
            em = discord.Embed(color = ctx.author.color)
            em.set_author(name=guild, icon_url=self.client.user.display_avatar.url) 
            em.set_thumbnail(url=self.client.user.display_avatar.url)
        em.add_field(name="Owner", value=guild.owner, inline=False)
        em.add_field(name="Created on", value=f"`{guild.created_at.strftime('%a, %b %d, %Y | %H:%M %p')}`", inline=False)
        em.add_field(name="Members", value=f"{len(guild.members)}") 
        em.add_field(name="Roles", value=f"{len(guild.roles)}") 
        em.set_footer(text=f"ID: {guild.id} | {guild}")
        
        if guild.banner:
            em.set_image(url=guild.banner.url)
        await ctx.send(embed=em)
    
    
    @admin.command()
    async def stats(self, ctx):
        em = discord.Embed(color=discord.Colour.random())
        em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
        em.add_field(name="Ping", value=f"{round(self.client.latency * 1000)}ms", inline=False)
        em.add_field(name="Users", value=len(self.client.users), inline=False)
        em.add_field(name="Guilds", value=len(self.client.guilds), inline=False)
        await ctx.send(embed=em)
    
    @admin.command(name="eval", description="Executes.", aliases=["execute"])
    async def calculate(self, ctx,*, equation):
        value = eval(equation)
        await ctx.reply(f"```py\n{value}```", mention_author=False)
    
    @admin.command(name="premium", description="Toggles premium")
    @commands.is_owner()
    async def premium(self, ctx):
        db = sqlite3.connect("data/database/Configs.db")
        cr = db.cursor()
        cr.execute(f'''SELECT Premium FROM Configs WHERE Guild = {ctx.guild.id}''')
        pr = cr.fetchone()[0]
        if not pr:
            cr.execute(f'''UPDATE Configs SET Premium = 1 WHERE Guild = {ctx.guild.id}''')
            await ctx.send(f"{self.client.success} | Successfully **enabled** premium for the guild `{ctx.guild.id}`.")
        else:
            cr.execute(f'''UPDATE Configs SET Premium = 0 WHERE Guild = {ctx.guild.id}''')
            await ctx.send(f"{self.client.success} | Successfully **disabled** premium for the guild `{ctx.guild.id}`.")
        db.commit()
        db.close()
    
async def setup(client):
    await client.add_cog(Admin(client))