import aiosqlite

from discord.ext import commands

from utils import config


class Configs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = "data/database/configs.db"
        self.emoji = "<:Ecog:1127303860227154000>"
    
    @commands.Cog.listener("on_ready")
    async def setup_config(self):

        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""CREATE TABLE IF NOT EXISTS Configs(
            Guild integer,
            Prefix text,
            'No prefix' integer,
            Premium integer,
            Voice integer,
            LoopSong integer,
            LoopPlaylist integer
            )""")
            await db.commit()
        
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT Guild FROM Configs""") as c:
                data = await c.fetchall()
                guild_ids = [x[0] for x in data]

                for guild in self.bot.guilds:
                    if not guild.id in guild_ids:
                        await db.execute(f"""INSERT INTO Configs(
                        Guild, Prefix, 'No prefix', Premium, Voice, LoopSong, LoopPlaylist)
                        VALUES(?, ?, ?, ?, ?, ?, ?)""", (guild.id, config.prefix, 0, 0, 0, 0, 0))
            await db.commit()
    
    
    @commands.Cog.listener("on_guild_join")
    async def create_new_config(self, guild):

        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT Guild FROM Configs""") as c:
                data = await c.fetchall()
                guild_ids = [x[0] for x in data]

                if not guild.id in guild_ids:
                    await db.execute(f"""INSERT INTO Configs(
                    Guild, Prefix, 'No prefix', Premium, Voice, LoopSong, LoopPlaylist)
                    VALUES(?, ?, ?, ?, ?, ?, ?)""", (guild.id, config.prefix, 0, 0, 0, 0, 0))
            await db.commit()
    
    
    @commands.hybrid_group(name="prefix", description="Configures prefix for your server.", usage="prefix <set/off>")
    async def prefix(self, ctx):
        return
    
    @prefix.command(name="set", description="Sets a custom prefix for your server.", usage="prefix set <new prefix>")
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, prefix: str):

        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""UPDATE Configs SET Prefix = ?, 'No prefix' = ? WHERE Guild = {ctx.guild.id}""", (str(prefix), 0))
            await db.commit()

        await ctx.send(f"{self.bot.success} | Prefix was changed to `{prefix}`.")
    
    @prefix.command(name="off", description="Sets no prefix for your server.", usage="prefix off")
    @commands.has_permissions(manage_guild=True)
    async def off(self, ctx):

        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""UPDATE Configs SET 'No prefix' = 1 WHERE Guild = {ctx.guild.id}""")
            await db.commit()

        await ctx.send(f"{self.bot.success} | Successfully enabled no prefix for the guild `{ctx.guild.id}`.")
    
    
async def setup(bot):
    await bot.add_cog(Configs(bot))