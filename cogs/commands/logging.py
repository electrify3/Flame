import asyncio

import discord
import aiosqlite

from discord.ext import commands

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Elogging:1141365823722754069>"
        self.path = "data/database/Logging.db"
        asyncio.run_coroutine_threadsafe(self.create_table(), self.bot.loop)
    
    async def create_table(self):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("""CREATE TABLE IF NOT EXISTS Logging(
                Guild integer,
                Server integer,
                Moderation integer,
                Member integer,
                Message integer,
                Invite integer,
                'Join' integer,
                Leave integer,
                Role integer,
                Ban integer,
                Voice integer
            )"""):
                await db.commit()
    
    
    async def setuplog(self, ctx, category, channel):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""UPDATE Logging SET '{category}' = {channel.id} WHERE Guild = {ctx.guild.id}"""):
                await db.commit()
        await ctx.send(f"{self.bot.success} | {category.capitalize()} log is now set to {channel.mention}.")
    
    
    @commands.Cog.listener("on_ready")
    async def check_database(self):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("""SELECT Guild FROM Logging""") as c:
                data = await c.fetchall()
                data = [x[0] for x in data]
                for guild in self.bot.guilds:
                    if guild.id not in data:
                        await db.execute("""INSERT INTO Logging(
                            Guild, Server, Moderation, Member, Message, Invite, 'Join', Leave, Role, Ban, Voice)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (guild.id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                await db.commit()

    @commands.Cog.listener("on_guild_join")
    async def update_database(self, guild):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("""SELECT Guild FROM Logging""") as c:
                data = await c.fetchall()
                data = [x[0] for x in data]
                if guild.id not in data:
                    await db.execute("""INSERT INTO Logging(
                        Guild, Server, Moderation, Member, Message, Invite, 'Join', Leave, Role, Ban, Voice)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (guild.id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                await db.commit()
    
    
    @commands.hybrid_command(name="serverlog", description="Set server log channel.", usage="serverlog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def serverlog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Server", channel)
    
    @commands.hybrid_command(name="moderationlog", description="Set moderation log channel.", usage="moderationlog", aliases=["modlog"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def moderationlog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Moderation", channel)
    
    @commands.hybrid_command(name="memberlog", description="Set member log channel.", usage="memberlog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def memberlog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Member", channel)
    
    @commands.hybrid_command(name="messagelog", description="Set message log channel.", usage="messagelog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def messagelog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Message", channel)

    @commands.hybrid_command(name="invitelog", description="Set invite log channel.", usage="invitelog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def invitelog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Invite", channel)

    @commands.hybrid_command(name="joinlog", description="Set join log channel.", usage="joinlog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def joinlog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Join", channel)

    @commands.hybrid_command(name="leavelog", description="Set leave log channel.", usage="leavelog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leavelog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Leave", channel)

    @commands.hybrid_command(name="rolelog", description="Set role log channel.", usage="rolelog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def rolelog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Role", channel)

    @commands.hybrid_command(name="banlog", description="Set ban log channel.", usage="banlog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def banlog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Ban", channel)

    @commands.hybrid_command(name="voicelog", description="Set voice log channel.", usage="voicelog")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def voicelog(self, ctx, channel: discord.TextChannel):
        await self.setuplog(ctx, "Voice", channel)
    
    @commands.hybrid_command(name="disablelog", description="Disable log categories.", usage="disablelog <category1 category2 ... | all>")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def disablelog(self, ctx, *, categories):
        categories = [*set(categories.lower().split(" "))]
        valid = ["Server", "Moderation", "Member", "Message", "Invite", "Join", "Leave", "Role", "Ban", "Voice"]
        if "all" == categories[0]:
            categories = valid
        invalid = [category for category in categories if category.capitalize() not in valid]
        if invalid:
            return await ctx.send(f"{self.bot.warning} | The following categories are not valid: {', '.join(invalid)}!")
        async with aiosqlite.connect(self.path) as db:
            for category in categories:
                async with db.execute(f"""UPDATE Logging SET '{category.capitalize()}' = 0 WHERE Guild = {ctx.guild.id}"""):
                    await db.commit()
        await ctx.send(f"{self.bot.success} | Disabled log categories: {', '.join(category.capitalize() for category in categories)}.")
    
    @commands.hybrid_command(name="viewlogs", description="View current log settings.", usage="viewlogs")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def viewlogs(self, ctx):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT * FROM Logging WHERE Guild = {ctx.guild.id}""") as c:
                data = await c.fetchone()

        settings = {
            "Server": data[1],
            "Moderation": data[2],
            "Member": data[3],
            "Message": data[4],
            "Invite": data[5],
            "Join": data[6],
            "Leave": data[7],
            "Role": data[8],
            "Ban": data[9],
            "Voice": data[10]
        }
        
        if not [channelid for channelid in settings.values() if channelid]:
            return await ctx.send(f"{self.bot.warning} | There is no log channel set in this server!")
        embed = discord.Embed(title="Log Settings", color=self.bot.color)
        embed.set_thumbnail(url=(ctx.guild.icon or ctx.me.display_avatar).url)
        for category, channelid in settings.items():
            if channelid:
                embed.add_field(name=category, value=f"<#{channelid}>", inline=False)
        embed.set_footer(text=f'Requested by: {ctx.author.name}')
        await ctx.send(embed=embed)
    
    
async def setup(bot):
    await bot.add_cog(Logging(bot))