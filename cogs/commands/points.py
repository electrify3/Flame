import discord
import sqlite3

from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

class Controller(View):
	def __init__(self, ctx, data, current, max):
		super().__init__(
		timeout = 120
		)
		self.ctx = ctx
		self.data = data
		self.current = current
		self.max = max
		self.message = None
	
	
	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
			return False
		else:
			return True
	
	
	async def on_timeout(self):
		for children in self.children:
			children.disabled = True
		await self.message.edit(view=self)
	
	
	def set_view(self):
		if self.current == 1:
			self.children[0].disabled = True
			self.children[1].disabled = True
			self.children[2].disabled = False
			self.children[3].disabled = False
		elif self.current == self.max:
			self.children[0].disabled = False
			self.children[1].disabled = False
			self.children[2].disabled = True
			self.children[3].disabled = True
		else:
			self.children[0].disabled = False
			self.children[1].disabled = False
			self.children[2].disabled = False
			self.children[3].disabled = False
	
	@staticmethod
	async def get_embed(ctx, data, page):
		entries_per_page = 10
		max_pages = (len(data) - 1) // entries_per_page + 1
		
		start_index = (page - 1) * entries_per_page
		end_index = start_index + entries_per_page
		leaderboard_page = data[start_index:end_index]
		
		user_list = []
		for rank, value in enumerate(leaderboard_page, start=start_index):
			user = f"<@{value[0]}>"
			sentence = f"{rank+1}. {user}:\t {value[1]} points."
			user_list.append(sentence)
			
		description = "\n".join(data for data in user_list)
		embed = discord.Embed(title="Points Leaderboard",description=description, color=ctx.bot.color)
		embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else ctx.me.display_avatar.url)
		embed.set_footer(text=f"Page {page}/{max_pages}\t | \tUse {ctx.prefix}points to view your points.")
		return embed
	
	
	@discord.ui.button(emoji="<:Edoublearrow2:1180724072678694962>", disabled=True)
	async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		self.current = 1
		self.set_view()
		em = await self.get_embed(self.ctx, self.data, self.current)
		return await interaction.message.edit(embed=em, view=self)
		
	
	@discord.ui.button(emoji="<:Earrow2:1180723707279315057>", disabled=True)
	async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		self.current -= 1
		self.set_view()
		em = await self.get_embed(self.ctx, self.data, self.current)
		return await interaction.message.edit(embed=em, view=self)
		
	
	@discord.ui.button(emoji="<:Earrow:1127175875549462602>")
	async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		self.current += 1
		self.set_view()
		em = await self.get_embed(self.ctx, self.data, self.current)
		return await interaction.message.edit(embed=em, view=self)
	
	
	@discord.ui.button(emoji="<:Edoublearrow:1180723248388902933>")
	async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		self.current = self.max
		self.set_view()
		em = await self.get_embed(self.ctx, self.data, self.current)
		return await interaction.message.edit(embed=em, view=self)





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
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""UPDATE '{self.ctx.guild.id} Points' SET points = points+{self.value} WHERE id = {self.ctx.author.id}""")
		c.execute(f"""UPDATE '{self.ctx.guild.id} Points' SET points = points-{self.value} WHERE id = {self.user.id}""")
		c.execute(f"""UPDATE '{self.ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
		db.commit()
		db.close()
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
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""VACUUM""")
		c.execute(f"""DELETE FROM '{self.ctx.guild.id} Points'""")
		db.commit()
		db.close()
		await interaction.message.edit(content=f"{interaction.client.success} | Successfully cleared everyone points.", embed=None, view=None)
		self.stop()
		
	@discord.ui.button(label='Abort', style=discord.ButtonStyle.red)
	async def abort(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		await interaction.message.edit(content=f"{interaction.client.warning} | Action aborted!", embed=None, view=None)
		self.stop()




class Points(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.emoji = "<:Elist:1127305243978371245>"
		self.path = "data/database/Points.db"
	
	
	def setup_user(self, guild, user):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""
		SELECT points FROM '{guild} Points' WHERE id = {user}""")
		data = c.fetchone()
		
		if not data:
			c.execute(f"""INSERT INTO '{guild} Points'(
			id, points)
			VALUES
			(?, ?)""", (user, 0))
		db.commit()
		db.close()
	
	
	def get_data(self, guild, user):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""
		SELECT * FROM '{guild} Points' WHERE id = {user}""")
		data = c.fetchone()
		db.commit()
		db.close()
		return data
	
	
	def get_rank(self, guild, user):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""
		SELECT * FROM '{guild} Points' ORDER BY points DESC""")
		data = c.fetchall()
		db.commit()
		db.close()
		user = self.get_data(guild, user)
		rank = None
		for index, entry in enumerate(data):
			if user[0] in entry and not user[1] <= 0:
				rank = index +1
				break
		return rank
	
	
	@commands.Cog.listener("on_ready")
	async def create_table(self):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		for guild in self.client.guilds:
			c.execute(f"""CREATE TABLE IF NOT EXISTS '{guild.id} Points'(
			id integer,
			points integer
			)""")
			c.execute(f"""CREATE INDEX IF NOT EXISTS idx_points_{guild.id} ON '{guild.id} Points' (points)""")
		db.commit()
		db.close()
	
	
	@commands.Cog.listener("on_guild_join")
	async def create_new(self, guild):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""CREATE TABLE IF NOT EXISTS '{guild.id} Points'(
		id integer,
		points integer
		)""")
		c.execute(f"""CREATE INDEX IF NOT EXISTS idx_points_{guild.id} ON '{guild.id} Points' (points)""")
		db.commit()
		db.close()
	
	
	@commands.hybrid_group(name="points", description="Display user points.", usage="points [user/id]")
	@commands.guild_only()
	@app_commands.describe(user="Select a user.")
	async def points(self, ctx, user: discord.User=commands.Author):
		self.setup_user(ctx.guild.id, user.id)
		data = self.get_data(ctx.guild.id, user.id)[1]
		rank = self.get_rank(ctx.guild.id, user.id)
		em = discord.Embed(color=self.client.color)
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
		self.setup_user(ctx.guild.id, user.id)
		data = self.get_data(ctx.guild.id, user.id)[1]
		rank = self.get_rank(ctx.guild.id, user.id)
		em = discord.Embed(color=self.client.color)
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
			return await ctx.reply(f"{self.client.warning} | You can't log against a bot.")
		elif user == ctx.author:
			return await ctx.reply(f"{self.client.warning} | You can't log against yourself.")
			
		self.setup_user(ctx.guild.id, ctx.author.id)
		self.setup_user(ctx.guild.id, user.id)
		
		view = Logger(ctx, user, value, self.path)
		view.message = await ctx.send(f"Hey, {user.mention}👋\n`{ctx.author}` wants to log **{value}** point(s) against you if you agree with this log, please react with agree button below.", view=view, mention_author=False)
	
	
	@points.command(name="update", description="Update a user points.", usage="points update <user/id> <value>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@app_commands.describe(user="Select a user.", value="New Points")
	async def update(self, ctx, user: discord.User, value: int):
		self.setup_user(ctx.guild.id, user.id)
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = {value} WHERE id = {user.id}""")
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
		db.commit()
		db.close()
		await ctx.send(f"{self.client.success} | Successfully updated `{user}` points to **{value}**.")
	
	
	@points.command(name="add", description="Add points to the user.", usage="points add <user/id> <value>")
	@commands.has_permissions(manage_guild=True)
	@commands.guild_only()
	@app_commands.describe(user="Select a user.", value="Points")
	async def add(self, ctx, user: discord.User, value: int):
		self.setup_user(ctx.guild.id, user.id)
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = points+{value} WHERE id = {user.id}""")
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
		db.commit()
		db.close()
		await ctx.send(f"{self.client.success} | Successfully added **{value}** points to `{user}`.")
	
	
	@points.command(name="remove", description="Remove points from the user.", usage="points remove <user/id> <value>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@app_commands.describe(user="User whose points you want to remove.", value="How much points you want to remove?")
	async def remove(self, ctx, user: discord.User, value: int):
		self.setup_user(ctx.guild.id, user.id)
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = points-{value} WHERE id = {user.id}""")
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = 0 WHERE points < 0""")
		db.commit()
		db.close()
		await ctx.send(f"{self.client.success} | Successfully removed **{value}** points from `{user}`.")
	
	
	
	
	@points.command(name="leaderboard", description="Display points leaderboard.", aliases=["lb"], usage="points leaderboard")
	@commands.guild_only()
	@app_commands.describe(page="Page of the leaderboard.")
	async def leaderboard(self, ctx, page: int=1):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""SELECT * FROM '{ctx.guild.id} Points' ORDER BY points DESC""")
		data = c.fetchall()
		db.commit()
		db.close()
		entries_per_page = 10
		max_pages = (len(data) - 1) // entries_per_page + 1
		
		if page < 1 or page > max_pages:
			return await ctx.send(f"{self.client.fail} | Page **{page}** not found.")
		
		embed = await Controller.get_embed(ctx, data, page)
		view = Controller(ctx, data, page, max_pages)
		view.message = await ctx.send(embed=embed, view=view)
	
	
	
	@points.command(name="clear", description="Reset points of a user.", usage="points clear <user/id>")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	@app_commands.describe(user="User whose points you want to reset.")
	async def clear(self, ctx, user: discord.User):
		self.setup_user(ctx.guild.id, user.id)
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""UPDATE '{ctx.guild.id} Points' SET points = {0} WHERE id = {user.id}""")
		db.commit()
		db.close()
		await ctx.send(f"{self.client.success} | Successfully cleared all points of `{user}`.")
	
	
	@points.command(name="reset", description="Reset the server leaderboards.", usage="points reset")
	@commands.guild_only()
	@commands.has_permissions(administrator=True)
	async def reset(self, ctx):
		em = discord.Embed(title="Are you sure?", description="This action is completely irreversible, click on reset to continue.", color=self.client.color)
		view = Reset(ctx, self.path)
		view.message = await ctx.send(embed=em, view=view)
	
	
async def setup(client):
	await client.add_cog(Points(client))