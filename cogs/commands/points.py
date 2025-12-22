import aiosqlite
import discord

from discord import app_commands
from discord.ext import commands
from discord.ui import View

from utils.paginator import Paginator


class Controller(Paginator):
    def __init__(self, ctx, items, page, max_pages):
        super().__init__(ctx, items, page, max_pages)

    def make_page(self):
        description = "\n".join(data for data in self.items[self.page*10-10:self.page*10])
        embed = discord.Embed(title="Points Leaderboard", description=description[:4000], color=self.ctx.bot.color)
        embed.set_author(name=self.ctx.me, icon_url=self.ctx.me.display_avatar.url)
        embed.set_footer(text=f"Page {self.page}/{self.max_pages}\t | \tUse {self.ctx.prefix}points to view your points.")
        return embed



class Logger(View):
    def __init__(self, ctx, user, value, path):
        super().__init__(
        timeout = 30
        )
        self.ctx = ctx
        self.user = user
        self.path = path
        self.value = value
        self.message = None
    
    async def on_timeout(self):
        await self.message.edit(content=f"{self.ctx.bot.fail} | No confirmation found in last 30seconds.", embed =None, view=None)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message(f"{interaction.client.warning} | You can't perform this action!", ephemeral=True)
            return False
        else:
            return True
    
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""UPDATE '{self.ctx.guild.id} Points' SET points = points+{self.value} WHERE id = {self.ctx.author.id}""")
            await db.execute(f"""UPDATE '{self.ctx.guild.id} Points' SET points = points-{self.value} WHERE id = {self.user.id}""")
            await db.execute(f"""UPDATE '{self.ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
            await db.commit()

        await interaction.message.edit(content=f"{interaction.client.success} | Log was successful!.", view=None)
        self.stop()
    
    @discord.ui.button(label='Abort', style=discord.ButtonStyle.red)
    async def abort(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.edit(content=f"{interaction.client.warning} | Log was aborted by `{self.user}`!", embed=None, view=None)
        self.stop()



class Reset(View):
    def __init__(self, ctx, path):
        super().__init__(
        timeout = 30
        )
        self.ctx = ctx
        self.path = path
        self.message = None
    
    async def on_timeout(self):
        await self.message.edit(content=f"{self.ctx.bot.fail} | No confirmation found in last 30seconds.", embed =None, view=None)
    
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            return False
        else:
            return True
    
    @discord.ui.button(label='Reset', style=discord.ButtonStyle.green)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""VACUUM""")
            await db.execute(f"""DELETE FROM '{self.ctx.guild.id} Points'""")
            await db.commit()

        await interaction.message.edit(content=f"{interaction.client.success} | Successfully cleared everyone points.", embed=None, view=None)
        self.stop()
        
    @discord.ui.button(label='Abort', style=discord.ButtonStyle.red)
    async def abort(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.edit(content=f"{interaction.client.warning} | Action aborted!", embed=None, view=None)
        self.stop()




class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Elist:1127305243978371245>"
        self.path = "data/database/points.db"
    
    
    async def setup_user(self, guild, user):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT points FROM '{guild} Points' WHERE id = {user}""") as c:
                data = await c.fetchone()
        
                if not data:
                    await db.execute(f"""INSERT INTO '{guild} Points'(
                    id, points)
                    VALUES
                    (?, ?)""", (user, 0))
            await db.commit()
    
    
    async def get_data(self, guild, user):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT * FROM '{guild} Points' WHERE id = {user}""") as c:
                data = await c.fetchone()
        return data
    
    
    async def get_rank(self, guild, user):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT * FROM '{guild} Points' ORDER BY points DESC""") as c:
                data = await c.fetchall()
        
        user = await self.get_data(guild, user)
        rank = None
        for index, entry in enumerate(data):
            if user[0] in entry and not user[1] <= 0:
                rank = index +1
                break
        return rank
    
    
    @commands.Cog.listener("on_ready")
    async def create_table(self):
        async with aiosqlite.connect(self.path) as db:
            for guild in self.bot.guilds:
                await db.execute(f"""CREATE TABLE IF NOT EXISTS '{guild.id} Points'(
                id integer,
                points integer
                )""")
                await db.execute(f"""CREATE INDEX IF NOT EXISTS idx_points_{guild.id} ON '{guild.id} Points' (points)""")
            await db.commit()
    
    
    @commands.Cog.listener("on_guild_join")
    async def create_new(self, guild):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""CREATE TABLE IF NOT EXISTS '{guild.id} Points'(
            id integer,
            points integer
            )""")
            await db.execute(f"""CREATE INDEX IF NOT EXISTS idx_points_{guild.id} ON '{guild.id} Points' (points)""")
            await db.commit()
    
    
    @commands.hybrid_group(name="points", description="Display user points.", usage="points [user/id]")
    @commands.guild_only()
    @app_commands.describe(user="Select a user.")
    async def points(self, ctx, user: discord.User=commands.Author):
        await self.setup_user(ctx.guild.id, user.id)
        data = await self.get_data(ctx.guild.id, user.id)[1]
        rank = await self.get_rank(ctx.guild.id, user.id)
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{user}'s points")
        em.set_thumbnail(url=user.display_avatar.url)
        em.add_field(name="Points", value=data, inline=False)
        em.add_field(name="Rank", value=rank, inline=False)
        em.set_footer(text=f"Use {ctx.prefix}points lb for leaderboard.")
        await ctx.send(embed=em)
    
    
    @points.command(name="view", description="Display user points.", usage="points view [user/id]")
    @commands.guild_only()
    @app_commands.describe(user="Select a user.")
    async def view(self, ctx, user: discord.User=commands.Author):
        await self.setup_user(ctx.guild.id, user.id)
        data = await self.get_data(ctx.guild.id, user.id)[1]
        rank = await self.get_rank(ctx.guild.id, user.id)
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{user}'s points")
        em.set_thumbnail(url=user.display_avatar.url)
        em.add_field(name="Points", value=data, inline=False)
        em.add_field(name="Rank", value=rank, inline=False)
        em.set_footer(text=f"Use {ctx.prefix}points lb for leaderboard.")
        await ctx.send(embed=em)
    
    
    @points.command(name="log", description="Log points to the user.", usage="points log <user/id> <value>")
    @commands.guild_only()
    @app_commands.describe(user="Select a user.", value="Points")
    async def log(self, ctx, user: discord.User, value: int=1):
        if user.bot:
            return await ctx.reply(f"{self.bot.warning} | You can't log against a bot.")
        elif user == ctx.author:
            return await ctx.reply(f"{self.bot.warning} | You can't log against yourself.")
            
        await self.setup_user(ctx.guild.id, ctx.author.id)
        await self.setup_user(ctx.guild.id, user.id)
        
        view = Logger(ctx, user, value, self.path)
        view.message = await ctx.send(f"Hey, {user.mention}👋\n`{ctx.author}` wants to log **{value}** point(s) against you if you agree with this log, please react with agree button below.", view=view, mention_author=False)
    
    
    @points.command(name="update", description="Update a user points.", usage="points update <user/id> <value>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(user="Select a user.", value="New Points")
    async def update(self, ctx, user: discord.User, value: int):
        await self.setup_user(ctx.guild.id, user.id)
        async with aiosqlite.connect(self.path) as db:

            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = {value} WHERE id = {user.id}""")
            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
            await db.commit()
        
        await ctx.send(f"{self.bot.success} | Successfully updated `{user}` points to **{value}**.")
    
    
    @points.command(name="add", description="Add points to the user.", usage="points add <user/id> <value>")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @app_commands.describe(user="Select a user.", value="Points")
    async def add(self, ctx, user: discord.User, value: int):
        await self.setup_user(ctx.guild.id, user.id)
        async with aiosqlite.connect(self.path) as db:

            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = points+{value} WHERE id = {user.id}""")
            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
            await db.commit()
        
        await ctx.send(f"{self.bot.success} | Successfully added **{value}** points to `{user}`.")
    
    
    @points.command(name="remove", description="Remove points from the user.", usage="points remove <user/id> <value>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(user="User whose points you want to remove.", value="How much points you want to remove?")
    async def remove(self, ctx, user: discord.User, value: int):
        await self.setup_user(ctx.guild.id, user.id)
        async with aiosqlite.connect(self.path) as db:

            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = points-{value} WHERE id = {user.id}""")
            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
            await db.commit()

        await ctx.send(f"{self.bot.success} | Successfully removed **{value}** points from `{user}`.")
    
    
    
    @points.command(name="leaderboard", description="Display points leaderboard.", aliases=["lb"], usage="points leaderboard [page]")
    @commands.guild_only()
    @app_commands.describe(page="Page of the leaderboard.")
    async def leaderboard(self, ctx, page: int = 1):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute(f"""SELECT * FROM '{ctx.guild.id} Points' ORDER BY points DESC""") as c:    
                data = await c.fetchall()

        max_pages = len(data)//10
        if max_pages <= len(data)/10:
            max_pages += 1
        
        if page < 0 or page > max_pages or not data:
            return await ctx.send(f"{self.bot.fail} | Page **{page}** not found.")
        
        
        entries = []

        for rank, value in enumerate(data, start=1):
            sentence = f"{rank}. <@{value[0]}>:\t {value[1]} points."
            entries.append(sentence)

        
        view = Controller(ctx, entries, page, max_pages)
        embed = view.make_page()
        view.set_view()
        view.message = await ctx.send(embed=embed, view=view)
    
    
    
    @points.command(name="clear", description="Reset points of a user.", usage="points clear <user/id>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(user="User whose points you want to reset.")
    async def clear(self, ctx, user: discord.User):
        await self.setup_user(ctx.guild.id, user.id)
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = {0} WHERE id = {user.id}""")
            await db.commit()
        await ctx.send(f"{self.bot.success} | Successfully cleared all points of `{user}`.")
    
    
    @points.command(name="reset", description="Reset the server leaderboards.", usage="points reset")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        em = discord.Embed(title="Are you sure?", description="This action is completely irreversible, click on reset to continue.", color=self.bot.color)
        view = Reset(ctx, self.path)
        view.message = await ctx.send(embed=em, view=view)
    
    
async def setup(bot):
    await bot.add_cog(Points(bot))