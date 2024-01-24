import yt_dlp
import discord

import sqlite3
import asyncio

from utils import tools
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button



class LoopButtons(View):
	def __init__(self, ctx, configpath):
		super().__init__(
		timeout = 30
		)
		self.ctx = ctx
		self.message = None
		self.configpath = configpath
	
	async def on_timeout(self):
		await self.message.edit(content=f"{self.ctx.bot.fail} | No response found in last 30seconds.", embed=None,view=None)
	
	
	async def interaction_check(self, interaction: discord.Interaction):
		if interaction.user != self.ctx.author:
			await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
			return False
		else:
			return True
	
	@discord.ui.button(label='Song Loop', emoji="🔁", style=discord.ButtonStyle.blurple)
	async def songloop(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		c.execute(f'''SELECT LoopSong FROM Configs WHERE Guild = {self.ctx.guild.id}''')
		loop = c.fetchone()[0]
		if loop:
			c.execute(f"""UPDATE Configs SET LoopSong = 0 WHERE Guild = {self.ctx.guild.id}""")
			await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled `song loop` mode.", embed=None, view=None)
		else:
			c.execute(f"""UPDATE Configs SET LoopSong = 1 WHERE Guild = {self.ctx.guild.id}""")
			await self.message.edit(content="<:Eonline:1137355060645466153> | Successfully enabled `song loop` mode.", embed=None, view=None)
		db.commit()
		db.close()
		self.stop()
		
	
	@discord.ui.button(label='Reset', emoji="⏹️", style=discord.ButtonStyle.red)
	async def resetloop(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		c.execute(f"""UPDATE Configs SET
				LoopSong = 0,
				LoopPlaylist = 0 WHERE Guild = {self.ctx.guild.id}""")
		await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled all `loop configs`.", embed=None, view=None)
		db.commit()
		db.close()
		self.stop()
	
	
	
	@discord.ui.button(label='Playlist Loop', emoji="🔂", style=discord.ButtonStyle.blurple)
	async def playlistloop(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		c.execute(f'''SELECT LoopPlaylist FROM Configs WHERE Guild = {self.ctx.guild.id}''')
		loop = c.fetchone()[0]
		if loop:
			c.execute(f"""UPDATE Configs SET LoopPlaylist = 0 WHERE Guild = {self.ctx.guild.id}""")
			await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled `playlist loop` mode.", embed=None, view=None)
		else:
			c.execute(f"""UPDATE Configs SET LoopPlaylist = 1 WHERE Guild = {self.ctx.guild.id}""")
			await self.message.edit(content="<:Eonline:1137355060645466153> | Successfully enabled `playlist loop` mode.", embed=None, view=None)
		db.commit()
		db.close()
		self.stop()


class Music(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.path = "data/database/Music.db"
		self.emoji = "<:Emusic:1165576153235460117>"
		self.configpath = "data/database/Configs.db"
		self.ydl_options = {
			'format': 'bestaudio/best',
			'quiet': True,
			'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
			'nocheckcertificate': True,
			'ignoreerrors': False,
			'logtostderr': False,
			'quiet': True,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'
			}
		self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
	
	
	def setup_song(self, ctx, term):
		with yt_dlp.YoutubeDL(self.ydl_options) as ydl:
			data = ydl.extract_info(f"ytsearch:{term}", download=False)["entries"][0]
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""SELECT * FROM '{ctx.guild.id} Music'""")  
		c.execute(f"""INSERT INTO '{ctx.guild.id} Music'(
			Requestor, Name, Author, Duration, Url, Thumbnail, Tags, Source)
			VALUES
			(?, ?, ?, ?, ?, ?, ?, ?)""", (str(ctx.author), str(data["title"]), str(data["channel"]), int(data["duration"]), str(data["webpage_url"]), str(data["thumbnail"]), str(data["tags"]), str(data["url"])))
		db.commit()
		db.close()
	
	
	
	def delete_song(self, id):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""VACUUM""")
		c.execute(f"""DELETE FROM `{id} Music` WHERE rowid = 1""")
		db.commit()
		db.close()
	
	def delete_all(self, id):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""DELETE FROM `{id} Music`""")
		db.commit()
		db.close()
	
	
	def get_data(self, id):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""SELECT * FROM '{id} Music'""")
		data = c.fetchone()
		db.close()
		return data
	
	def after_playing(self, ctx):
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		c.execute(f"""SELECT LoopSong, LoopPlaylist FROM Configs WHERE Guild = {ctx.guild.id}""")
		loop_config = c.fetchall()[0]
		db.close()
		
		if not loop_config[0]:
			if loop_config[1]:
				db = sqlite3.connect(self.path)
				c = db.cursor()
				try:
					c.execute(f"""INSERT INTO '{ctx.guild.id} Music'(
					Requestor, Name, Author, Duration, Url, Thumbnail, Tags, Source)
					VALUES
					(?, ?, ?, ?, ?, ?, ?, ?)""", self.get_data(ctx.guild.id))
				except: pass
				db.commit()
				db.close()
			self.delete_song(ctx.guild.id)
				
		data = self.get_data(ctx.guild.id)
		if not data:
			em = discord.Embed(title="End of queue", description="No song left to play.", color=discord.Colour.red())
			asyncio.run_coroutine_threadsafe(ctx.send(embed=em), self.client.loop)
			return
		if not ctx.voice_client.is_playing():
			
			em = discord.Embed(description=f"[{data[1]}]({data[4]})", color=discord.Colour.dark_theme())
			em.set_author(name="Now playing", icon_url=ctx.me.display_avatar.url)
			em.set_thumbnail(url=data[5])
			em.add_field(name="Channel", value=data[2], inline=False)
			em.add_field(name="Duration", value=tools.clean_time(data[3]), inline=False)
			em.set_footer(text=f"Use /queue for queue list.")
			source = asyncio.run(discord.FFmpegOpusAudio.from_probe(data[7], **self.ffmpeg_options))
			ctx.voice_client.play(source, after= lambda c: self.after_playing(ctx))
			asyncio.run_coroutine_threadsafe(ctx.send(embed=em), self.client.loop)
			
	
	async def check_player(self, ctx):
		if not ctx.voice_client:
			await ctx.send(f"{self.client.fail} | I am not connected to any voice channel.")
			return False
		if not ctx.author.voice:
			await ctx.send(f"{self.client.fail} | You are not connected to any voice channel.")
			return False
		if ctx.voice_client:
			if not ctx.voice_client.channel == ctx.author.voice.channel:
				await ctx.send(f"{self.client.fail} | I am connected to another voice channel.")
				return False
		return True
	
	
	@commands.Cog.listener("on_ready")
	async def setup_db(self):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		for guild in self.client.guilds:
			c.execute(f"""CREATE TABLE IF NOT EXISTS '{guild.id} Music'(
			Requestor text,
			Name text,
			Author text,
			Duration integer,
			Url text,
			Thumbnail text,
			Tags text,
			Source text
			)""")
		db.commit()
		db.close()
	
	
	@commands.Cog.listener("on_guild_join")
	async def create_new(self, guild):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""CREATE TABLE IF NOT EXISTS '{guild.id} Music'(
		Requestor text,
		Name text,
		Author text,
		Duration integer,
		Url text,
		Thumbnail text,
		Tags text,
		Source text
		)""")
		db.commit()
		db.close()
		
	
	@commands.Cog.listener("on_ready")
	async def initialise(self):
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		for guild in self.client.guilds:
			self.delete_all(guild.id)
			c.execute(f'''SELECT Voice FROM Configs WHERE Guild = {guild.id}''')
			ch = c.fetchone()
			if ch:
				try:
					vc = self.client.get_channel(ch[0])
					await vc.connect(self_deaf=True)
				except: continue
	
	@commands.Cog.listener("on_voice_state_update")
	async def clear_queue(self, member, before, after):
		if member is self.client.user and not after:
			self.delete_all(member.guild.id)
		
	
	
	@commands.hybrid_command(name="join", description="Joins a voice channel.", usage="join")
	@commands.guild_only()
	async def join(self, ctx):
		if not ctx.author.voice:
			await ctx.send(f"{self.client.warning} | You are not connected to any voice channel.")
			return
		if ctx.voice_client:
			await ctx.send(f"{self.client.warning} | I am already connected to a voice channel.")
			return
		else:
			await ctx.author.voice.channel.connect(self_deaf=True)
			await ctx.send(f"{self.client.success} | Successfully connected to `{ctx.author.voice.channel}`.")
	
	
	@commands.hybrid_command(name="disconnect", description="Leaves the voice channel.", aliases=["dc", "leave"], usage="disconnect")
	@commands.guild_only()
	@commands.has_guild_permissions(move_members=True)
	async def disconnect(self, ctx):
		if not ctx.voice_client:
			await ctx.send(f"{self.client.fail} | I am not connected to any voice channel.")
			return
		await ctx.voice_client.disconnect()
		await ctx.message.add_reaction('👋')
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		c.execute(f"""UPDATE Configs SET Voice = 0 WHERE Guild = {ctx.guild.id}""")
		db.commit()
		db.close()
	
	
	@commands.hybrid_command(name="queue", description="Shows the current queue.", aliases=["q"], usage="queue [page]")
	@commands.guild_only()
	@app_commands.describe(page="page no.")
	async def queue(self, ctx, page:int =1):
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""SELECT * FROM '{ctx.guild.id} Music'""")
		data = c.fetchall()
		db.commit()
		db.close()
		song_list = []
		
		max_pages = int((len(data)-1)/10)
		if max_pages < (len(data)-1)/10: max_pages += 1
			
		if page < 0 or page > max_pages or len(data) < 2:
			em = discord.Embed(title="Failed", description="No song in the queue.", color=discord.Colour.red())
			await ctx.send(embed=em)
			return
		
		for index, row in enumerate(data):
			if row is data[0]:
				continue
			song_list.append(f"{index}. [{row[1]}]({row[4]}) - `{row[0]}`\n")
		
		description = "\n".join(data for data in song_list[page*10-10:page*10])
		em = discord.Embed(title="Current Queue", description=description[:4000], color=discord.Colour.dark_theme())
		em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
		em.set_footer(text=f"Page {page}/{max_pages}")
		await ctx.send(embed=em)
	
	
	@commands.hybrid_command(name="remove", description="Removes a song from the queue.", usage="remove <song no.>")
	@commands.guild_only()
	@app_commands.describe(id="Position of song in the queue which you want to remove.")
	async def remove(self, ctx, id: int):
		if not self.check_player(ctx):
			return
		
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute(f"""SELECT * FROM '{ctx.guild.id} Music'""")
		data = c.fetchall()
		if len(data)-1 < id:
			await ctx.send(f"{self.client.fail} | No song found with id `{id}`.")
			return
		c.execute(f"""VACUUM""")
		c.execute(f"""DELETE FROM '{ctx.guild.id} Music' WHERE rowid = {id+1}""")
		
		db.commit()
		db.close()
		data = data[id]
		em = discord.Embed(title="Song Removed", description=f"[{data[1]}]({data[4]})", color=discord.Colour.dark_theme())
		em.set_footer(text=f"Removed by: {ctx.author}")
		await ctx.send(embed=em)
	
	
	@commands.hybrid_command(name="nowplaying", description="Display the current playing song.", aliases=["np"], usage="nowplaying")
	@commands.guild_only()
	async def nowplaying(self, ctx):
		data = self.get_data(ctx.guild.id)
		if not data:
			await ctx.send("{self.client.warning} | Currently no song is playing.")
			return
		em = discord.Embed(title="Now Playing", description=f"[{data[1]}]({data[4]})", color=discord.Colour.dark_theme())
		em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
		em.set_image(url=data[5])
		em.add_field(name="Channel", value=data[2], inline=False)
		em.add_field(name="Duration", value=tools.read_time(data[3]), inline=False)
		em.add_field(name="Requestor", value=f"`{data[0]}`", inline=False)
		youtube = Button(label="YouTube", url=data[4], emoji="<:Eyt:1166437726732701827>")
		view = View()
		view.add_item(youtube)
		await ctx.send(embed=em, view=view)
	
	
	@commands.hybrid_command(name="skip", description="Skips a song.", usage="skip")
	@commands.guild_only()
	async def skip(self, ctx):
		if not self.check_player(ctx):
			return
		if not ctx.voice_client.is_playing():
			await ctx.send(f"{self.client.fail} | Player is not playing anything.")
		
		data = self.get_data(ctx.guild.id)
		ctx.voice_client.stop()
		em = discord.Embed(title="Skipped", description=f"[{data[1]}]({data[4]})", color=discord.Colour.dark_theme())
		em.set_footer(text=f"Skipped by: {ctx.author}")
		await ctx.send(embed=em)
	
	
	@commands.hybrid_command(name="stop", description="Stop playing and clear the queue.", usage="stop")
	@commands.guild_only()
	@commands.has_permissions(manage_guild=True)
	async def stop(self, ctx):
		if not self.check_player(ctx):
			return
		
		data = self.get_data(ctx.guild.id)
		if not data:
			await ctx.send(f"{self.client.warning} | Queue is already empty.")
		self.delete_all(ctx.guild.id)
		await ctx.send(f"{self.client.success} | Successfully stopped the player and cleared the queue.")
		ctx.voice_client.stop()
		
	
	
	@commands.hybrid_command(name="play", description="Plays a song.", aliases=["p"], usage="play <term>")
	@commands.guild_only()
	@app_commands.describe(term="Song name or url which you want to play.")
	async def play(self, ctx, *, term):
		if not ctx.author.voice:
			await ctx.send(f"{self.client.fail} | You are not connected to any voice channel.")
			return
		if ctx.voice_client:
			if not ctx.voice_client.channel is ctx.author.voice.channel:
				await ctx.send(f"{self.client.fail} | I am already connected to a voice channel.")
				return
		else:
			await ctx.author.voice.channel.connect(self_deaf=True)
			await ctx.send(f"{self.client.success} | Successfully connected to `{ctx.author.voice.channel}`.")
		em = discord.Embed(title="Initialising the player", color=discord.Colour.dark_theme())
		message = await ctx.send(embed=em)
		term = term.strip("<>")
		self.setup_song(ctx, term)
		data = self.get_data(ctx.guild.id)
		
		em = discord.Embed(title="Searching", description=term, color=discord.Colour.dark_theme())
		message = await message.edit(embed=em)
		playing = ctx.voice_client.is_playing()
		if playing:
			db = sqlite3.connect(self.path)
			c = db.cursor()
			c.execute(f"""SELECT * FROM '{ctx.guild.id} Music'""")
			rows = c.fetchall()
			data = rows[-1]
			db.close()
			
		em = discord.Embed(description=f"[{data[1]}]({data[4]})", color=discord.Colour.dark_theme())
		em.set_author(name="Added to queue" if playing else "Now playing", icon_url=ctx.me.display_avatar.url)
		em.set_thumbnail(url=data[5])
		em.add_field(name="Channel", value=data[2], inline=False)
		em.add_field(name="Duration", value=tools.clean_time(data[3]), inline=False)
		if playing: em.add_field(name="Queue number", value=len(rows)-1, inline=False)
		em.set_footer(text=f"Requested by: {ctx.author}")
		if not playing:
			source = await discord.FFmpegOpusAudio.from_probe(data[7], **self.ffmpeg_options)
			ctx.voice_client.play(source, after= lambda c: self.after_playing(ctx))
		await message.edit(embed=em)
	
	
	
	@commands.hybrid_command(name="247", description="Toggles 24/7 music config.", usage="247")
	@commands.guild_only()
	@commands.has_guild_permissions(manage_guild=True)
	async def _247(self, ctx):
		if not self.check_player(ctx):
			return
		
		db = sqlite3.connect(self.configpath)
		c = db.cursor()
		c.execute(f'''SELECT Voice FROM Configs WHERE Guild = {ctx.guild.id}''')
		vchannel = c.fetchone()[0]
		
		if not vchannel:
			c.execute(f"""UPDATE Configs SET Voice = {ctx.voice_client.channel.id} WHERE Guild = {ctx.guild.id}""")
			await ctx.send("<:Eonline:1137355060645466153> | Successfully enabled `24/7` mode.")
		else:
			c.execute(f"""UPDATE Configs SET Voice = 0 WHERE Guild = {ctx.guild.id}""")
			await ctx.send("<:Ednd:1137355047752187944> | Successfully disabled `24/7` mode.")
		db.commit()
		db.close()
	
	
	@commands.hybrid_command(name="loop", description="Toggles loop music config.", usage="loop")
	@commands.guild_only()
	async def loop(self, ctx):
		if not self.check_player(ctx):
			return
		em = discord.Embed(title="Select a action", color=self.client.color)
		em.set_image(url="https://cdn.discordapp.com/attachments/1165698279334481980/1166047193069793431/select_one.png")
		view = LoopButtons(ctx, self.configpath)
		view.message = await ctx.send(embed=em, view=view)
	
	
async def setup(client):
	await client.add_cog(Music(client))