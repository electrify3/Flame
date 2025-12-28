from typing import TYPE_CHECKING

import aiosqlite
import discord
from discord.ext import commands

from utils import config

if TYPE_CHECKING:
    from main import Bot


class Admin(commands.Cog):
    def __init__(self, bot: 'Bot') -> None:
        self.bot: Bot = bot
        self.emoji = "<:Eadmin:1127307669301121144>"
    
    
    async def cog_check(self, ctx: commands.Context) -> bool:
        if ctx.author.id in config.admins:
            return True
        else:
            embed = discord.Embed(description=f'{self.bot.warning} | You are not an admin of this bot!', colour=self.bot.color)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed, ephemeral=True, delete_after=5)
            return False
    
    
    @commands.group(name="admin", description="Displays bot admins names.", usage='admin', invoke_without_command=True)
    async def admin(self, ctx: commands.Context) -> None:
        admins = [await self.bot.fetch_user(admin) for admin in config.admins]
        description = "\n".join(f"{a.mention} [{a}]" for a in admins)
        em = discord.Embed(title="Admins", description=description, color=discord.Colour.blurple())
        await ctx.send(embed=em)
    
    @admin.command(name='say', description='Echo\'s a text', usage='admin say <text>')
    async def say(self, ctx: commands.Context, *, text: str) -> None:
        await ctx.message.delete()
        await ctx.send(text)
    
    @admin.command(name='reply', description='replies to a given message.', usage='admin reply <message_id/url> <text>')
    async def reply(self, ctx: commands.Context, message : discord.Message, *, content: str) -> None:
        await ctx.message.delete()
        await message.reply(content) 
    
    
    @admin.command(name='guild', description='displays server info of a given server.', usage='admin guild <guild_id>')
    async def guild(self, ctx: commands.Context, guild: discord.Guild) -> None:

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
    
    
    @admin.command(name='stats', description='display bot statistics.', usage='admin stats')
    async def stats(self, ctx: commands.Context) -> None:
        em = discord.Embed(color=discord.Colour.random())
        em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
        em.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        em.add_field(name="Users", value=len(self.bot.users), inline=False)
        em.add_field(name="Guilds", value=len(self.bot.guilds), inline=False)
        await ctx.send(embed=em)
    

    @admin.command(name="premium", description="Toggles premium features for the guild.", usage='admin premium')
    @commands.is_owner()
    async def premium(self, ctx: commands.Context) -> None:
        async with aiosqlite.connect('data/database/configs.db') as db:
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


    @admin.command(name='extensions', description='shows all the loaded extensions.', usage='admin extensions')
    async def extensions(self, ctx: commands.Context) -> None:
        embed = discord.Embed(title='Loaded Extensions', colour=self.bot.color)
        embed.description = "\n".join(f"{index}. [`{extension}`]" for index, extension in enumerate(self.bot.extensions, start=1))
        await ctx.send(embed=embed)


    @admin.command(name='load', description='Loads an extension.', usage='admin load <name | path>')
    async def load(self, ctx: commands.Context, name: str) -> None:
        if name in self.bot.extensions:
            await ctx.send(f'{self.bot.warning} | Extension is already loaded! did you mean `{ctx.prefix}reload {name}`?')
        else:
            message = await ctx.send(f'{self.bot.working} | Loading extension `{name}`.')
            await self.bot.load_extension(name)
            await message.edit(content=f'{self.bot.success} | Loaded extension `{name}`.')
    

    @admin.command(name='unload', description='Unloads an extension.', usage='admin unload <name | path>')
    async def unload(self, ctx: commands.Context, name: str) -> None:
        if not name in self.bot.extensions:
            await ctx.send(f'{self.bot.warning} | Extension `{name}` is not loaded!')
        else:
            message = await ctx.send(f'{self.bot.working} | Unoading extension `{name}`.')
            await self.bot.unload_extension(name)
            await message.edit(content=f'{self.bot.success} | Unloaded extension `{name}`.')

    
    @admin.command(name='reload', description='Reloads an extension.', usage='admin reload <name | path>')
    async def reload(self, ctx: commands.Context, name: str) -> None:
        if not name in self.bot.extensions:
            await ctx.send(f'{self.bot.warning} | Extension `{name}` is not loaded!')
        else:
            message = await ctx.send(f'{self.bot.working} | Reoading extension `{name}`.')
            await self.bot.reload_extension(name)
            await message.edit(content=f'{self.bot.success} | Reloaded extension `{name}`.')


    @admin.command(name='refresh', description='Reloads all the extensions.', usage='refresh')
    async def refresh(self, ctx: commands.Context) -> None:
        message = await ctx.send(f'{self.bot.warning} | Refesh in progreess. it may take few moments.')
        extensions = list(self.bot.extensions)
        for extension in extensions:
            await self.bot.reload_extension(extension)
        await message.edit(content=f'{self.bot.success} | Reloaded all extensions.')

    
async def setup(bot: 'Bot') -> None:
    await bot.add_cog(Admin(bot))