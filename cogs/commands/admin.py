import aiosqlite

import discord
from discord.ext import commands

from utils import config


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Eadmin:1127307669301121144>"
    
    
    async def cog_check(self, ctx):
        if ctx.author.id in config.admins:
            return True
        else:
            raise "You are not a admin of this bot."
    
    
    @commands.group(name="admin", description="Displays bot admins names.", usage='admin', invoke_without_command=True)
    async def admin(self, ctx):
        admins = [await self.bot.fetch_user(admin) for admin in config.admins]
        description = "\n".join(f"{a.mention} [{a}]" for a in admins)
        em = discord.Embed(title="Admins", description=description, color=discord.Colour.blurple())
        await ctx.send(embed=em)
    
    @admin.command(name='say', description='Echo\'s a text', usage='say <text>')
    async def say(self, ctx,*, message=None):
        await ctx.message.delete()
        if message is None :
            reply = await ctx.send('No arguments provided!')
            await reply.delete(delay=5)
            return
        await ctx.send(f'{message}')
    
    @admin.command(name='reply', description='replies to a given message', usage='reply <message_id/url> <text>')
    async def reply(self, ctx, message : discord.Message,*, content):
        await ctx.message.delete()
        await message.reply(content) 
    
    
    @admin.command(name='guild', description='displays server info of a given server.', usage='guild <guild_id>')
    async def guild(self, ctx, guild: discord.Guild):
        if guild.icon:
            em = discord.Embed(description=f"[Server icon]({guild.icon.url})", color = ctx.author.color)
            em.set_author(name=guild, icon_url=guild.icon.url) 
            em.set_thumbnail(url=guild.icon.url)
        else:
            em = discord.Embed(color = ctx.author.color)
            em.set_author(name=guild, icon_url=self.bot.user.display_avatar.url) 
            em.set_thumbnail(url=self.bot.user.display_avatar.url)
        em.add_field(name="Owner", value=guild.owner, inline=False)
        em.add_field(name="Created on", value=f"`{guild.created_at.strftime('%a, %b %d, %Y | %H:%M %p')}`", inline=False)
        em.add_field(name="Members", value=f"{len(guild.members)}") 
        em.add_field(name="Roles", value=f"{len(guild.roles)}") 
        em.set_footer(text=f"ID: {guild.id} | {guild}")
        
        if guild.banner:
            em.set_image(url=guild.banner.url)
        await ctx.send(embed=em)
    
    
    @admin.command(name='stats', description='display bot statistics', usage='stats')
    async def stats(self, ctx):
        em = discord.Embed(color=discord.Colour.random())
        em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
        em.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        em.add_field(name="Users", value=len(self.bot.users), inline=False)
        em.add_field(name="Guilds", value=len(self.bot.guilds), inline=False)
        await ctx.send(embed=em)
    
    @admin.command(name="eval", description="Executes a python code.", aliases=["execute"], usage='eval')
    async def calculate(self, ctx,*, equation):
        value = eval(equation)
        await ctx.reply(f"```py\n{value}```", mention_author=False)
    

    @admin.command(name="premium", description="Toggles premium features for the guild", usage='premium')
    @commands.is_owner()
    async def premium(self, ctx: commands.Context):
        async with aiosqlite.connect('data/database/Configs.db') as db:
            async with db.execute(f'''SELECT Premium FROM Configs WHERE Guild = {ctx.guild.id}''') as c:
                data = await c.fetchone()
                is_premium = data[0]

            if is_premium:
                await db.execute(f'''UPDATE Configs SET Premium = 0 WHERE Guild = {ctx.guild.id}''')
                await db.commit()
                await ctx.send(f"{self.bot.success} | Successfully **disabled** premium for the guild `{ctx.guild.id}`.")
            else:
                await db.execute(f'''UPDATE Configs SET Premium = 1 WHERE Guild = {ctx.guild.id}''')
                await db.commit()
                await ctx.send(f"{self.bot.success} | Successfully **enabled** premium for the guild `{ctx.guild.id}`.")

    
async def setup(bot):
    await bot.add_cog(Admin(bot))