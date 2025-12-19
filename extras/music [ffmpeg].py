import asyncio

import aiosqlite
import discord
import yt_dlp

from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

from utils.tools import clean_time


class LoopButtons(View):
    def __init__(self, ctx, database):
        super().__init__(
        timeout = 30
        )
        self.ctx = ctx
        self.database = database
        self.message = None
    
    async def on_timeout(self):
        await self.message.edit(content=f"{self.ctx.bot.fail} | No response found in last 30seconds.", embed=None,view=None)
    
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label='Song Loop', emoji="🔁", style=discord.ButtonStyle.blurple)
    async def songloop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        loop = self.database[self.ctx.guild.id]['LoopSong']
        if loop:
            self.database[self.ctx.guild.id]['LoopSong'] = False
            await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled `song loop` mode.", embed=None, view=None)
        else:
            self.database[self.ctx.guild.id]['LoopSong'] = True
            await self.message.edit(content="<:Eonline:1137355060645466153> | Successfully enabled `song loop` mode.", embed=None, view=None)
        self.stop()
        
    
    @discord.ui.button(label='Reset', emoji="⏹️", style=discord.ButtonStyle.red)
    async def resetloop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.database[self.ctx.guild.id]['LoopSong'] = False
        self.database[self.ctx.guild.id]['LoopPlaylist'] = False
        await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled all `loop configs`.", embed=None, view=None)
        self.stop()
    
    
    
    @discord.ui.button(label='Playlist Loop', emoji="🔂", style=discord.ButtonStyle.blurple)
    async def playlistloop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        loop = self.database[self.ctx.guild.id]['LoopPlaylist']
        if loop:
            self.database[self.ctx.guild.id]['LoopPlaylist'] = False
            await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled `playlist loop` mode.", embed=None, view=None)
        else:
            self.database[self.ctx.guild.id]['LoopPlaylist'] = True
            await self.message.edit(content="<:Eonline:1137355060645466153> | Successfully enabled `playlist loop` mode.", embed=None, view=None)
        self.stop()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Emusic:1165576153235460117>"
        self.configpath = "data/database/configs.db"
        self.ydl_options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
            }
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -b:a 128k'}
        self.database = {}
    
    def set_structure(self, id):
        self.database[id] = {}
        self.database[id]['queue'] = []
        self.database[id]['LoopSong'] = False
        self.database[id]['LoopPlaylist'] = False
        self.database[id]['now_playing'] = None
        self.database[id]['host'] = None
    
    def setup_song(self, ctx, term):
        with yt_dlp.YoutubeDL(self.ydl_options) as ydl:
            rawdata = ydl.extract_info(f"ytsearch:{term}", download=False)['entries'][0]
            if not ctx.guild.id in self.database:
                self.set_structure(ctx.guild.id)

            data = {
                'requestor': ctx.author,
                'title': rawdata['title'],
                'author': rawdata['channel'],
                'url': rawdata['webpage_url'],
                'duration': int(rawdata['duration']),
                'thumbnail': rawdata['thumbnail'],
                'source': rawdata['url']

            }
            host = self.database[ctx.guild.id]['host']
            if not host:
                self.database[ctx.guild.id]['host'] = ctx.author
            self.database[ctx.guild.id]['queue'].append(data)
    
    def delete_song(self, id, index=0):
        return self.database[id]['queue'].pop(index)
    
    def delete_all(self, id):
        self.database[id]['queue'] = []
        self.database[id]['now_playing'] = None
        self.database[id]['host'] = None
    
    def get_song(self, id):
        queue = self.database[id]['queue']
        return queue[0] if queue else None
    
    def after_playing(self, ctx):
        # Loop handling
        if not self.database[ctx.guild.id]['LoopSong']:
            if self.database[ctx.guild.id]['LoopPlaylist']:
                data = self.get_song(ctx.guild.id)
                self.database[ctx.guild.id]['queue'].append(data)
            self.delete_song(ctx.guild.id)
        data = self.get_song(ctx.guild.id)
        if not data:
            em = discord.Embed(title="End of queue", description="No song left to play.", color=discord.Colour.red())
            asyncio.run_coroutine_threadsafe(ctx.send(embed=em), self.bot.loop)
            self.database[ctx.guild.id]['now_playing'] = None
            return
        
        if not ctx.voice_client.is_playing():
            em = discord.Embed(description=f"[{data['title']}]({data['url']})", color=discord.Colour.dark_theme())
            em.set_author(name="Now playing", icon_url=ctx.me.display_avatar.url)
            em.set_thumbnail(url=data['thumbnail'])
            em.add_field(name="Channel", value = data['author'], inline = False)
            em.add_field(name="Duration", value = clean_time(data['duration']), inline = False)
            em.set_footer(text=f"Requested by: {data['requestor']}")
            source = asyncio.run(discord.FFmpegOpusAudio.from_probe(data['source'], **self.ffmpeg_options))
            ctx.voice_client.play(source, after = lambda c: self.after_playing(ctx))
            asyncio.run_coroutine_threadsafe(ctx.send(embed=em), self.bot.loop)
            
    
    async def check_player(self, ctx):
        if not ctx.voice_client:
            await ctx.send(f"{self.bot.fail} | I am not connected to any voice channel.")
            return False
        if not ctx.author.voice:
            await ctx.send(f"{self.bot.fail} | You are not connected to any voice channel.")
            return False
        if ctx.voice_client:
            if not ctx.voice_client.channel == ctx.author.voice.channel:
                await ctx.send(f"{self.bot.fail} | I am connected to another voice channel.")
                return False
        return True
    
    @commands.Cog.listener("on_ready")
    async def initialise(self):
        async with aiosqlite.connect(self.configpath) as db:
            for guild in self.bot.guilds:
                self.set_structure(guild.id)
                async with db.execute(f'''SELECT Voice FROM Configs WHERE Guild = {guild.id}''') as c:
                    ch = await c.fetchone()
                    if ch:
                        try:
                            vc = self.bot.get_channel(ch[0])
                            await vc.connect(self_deaf=True)
                        except: continue
    

    @commands.Cog.listener("on_voice_state_update")
    async def clear_queue(self, member, before, after):
        if member == self.bot.user and not after:
            self.delete_all(member.guild.id)
        
    
    
    @commands.hybrid_command(name="join", description="Joins a voice channel.", usage="join")
    @commands.guild_only()
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f"{self.bot.warning} | You are not connected to any voice channel.")
            return
        if ctx.voice_client:
            await ctx.send(f"{self.bot.warning} | I am already connected to a voice channel.")
            return
        else:
            await ctx.author.voice.channel.connect(self_deaf=True)
            await ctx.send(f"{self.bot.success} | Successfully connected to `{ctx.author.voice.channel}`.")


    @commands.hybrid_command(name="disconnect", description="Leaves the voice channel.", aliases=["dc", "leave"], usage="disconnect")
    @commands.guild_only()
    @commands.has_guild_permissions(move_members=True)
    async def disconnect(self, ctx):
        if not ctx.voice_client:
            await ctx.send(f"{self.bot.fail} | I am not connected to any voice channel.")
            return
        await ctx.voice_client.disconnect()
        await ctx.send(f'{self.bot.success} | Successfully left the vc and destroyed the player.')

        async with aiosqlite.connect(self.configpath) as db:
            await db.execute(f"""UPDATE Configs SET Voice = 0 WHERE Guild = {ctx.guild.id}""")
            await db.commit()
    
    @commands.hybrid_command(name="queue", description="Shows the current queue.", aliases=["q"], usage="queue [page]")
    @commands.guild_only()
    @app_commands.describe(page="page no.")
    async def queue(self, ctx, page: int = 1):
        data = self.database[ctx.guild.id]['queue']
        songs = []
        
        max_pages = int((len(data)-1)/10)
        if max_pages < (len(data)-1)/10: max_pages += 1
            
        if page < 0 or page > max_pages or len(data) < 1:
            em = discord.Embed(title="Queue Empty", description="No song in the queue.", color=discord.Colour.red())
            await ctx.send(embed=em)
            return
        
        for index, song in enumerate(data):
            if song == data[0]:
                songs.append(f"▶️ Now Playing: [{song['title']}]({song['url']}) - `{song['requestor']}`\n")
                continue
            songs.append(f"{index}. [{song['title']}]({song['url']}) - `{song['requestor']}`\n")
        
        description = "\n".join(data for data in songs[page*10-10:page*10])
        em = discord.Embed(title="Current Queue", description=description[:4000], color=discord.Colour.dark_theme())
        em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
        em.set_footer(text=f"Page {page}/{max_pages}")
        await ctx.send(embed=em)


    @commands.hybrid_command(name="remove", description="Removes a song from the queue.", usage="remove <song no.>")
    @commands.guild_only()
    @app_commands.describe(id="Position of song in the queue which you want to remove.")
    async def remove(self, ctx, id: int):
        if not await self.check_player(ctx):
            return
        
        data = self.database[ctx.guild.id]['queue']
        if len(data)-1 < id:
            await ctx.send(f"{self.bot.fail} | No song found with id `{id}`.")
            return
        data = self.delete_song(ctx.guild.id, id)
        em = discord.Embed(title="Song Removed", description=f"[{data['title']}]({data['url']})", color=discord.Colour.dark_theme())
        em.set_footer(text=f"Removed by: {ctx.author}")
        await ctx.send(embed=em)
    

    @commands.hybrid_command(name="nowplaying", description="Display the current playing song.", aliases=["np"], usage="nowplaying")
    @commands.guild_only()
    async def nowplaying(self, ctx):
        data = self.get_song(ctx.guild.id)
        if not data:
            await ctx.send("{self.bot.warning} | Currently no song is playing.")
            return
        em = discord.Embed(title="Now Playing", description=f"[{data['title']}]({data['url']})", color=discord.Colour.dark_theme())
        em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
        em.set_image(url=data['thumbnail'])
        em.add_field(name="Channel", value=data['author'], inline=False)
        em.add_field(name="Duration", value=clean_time(data['duration']), inline=False)
        em.add_field(name="Requestor", value=f"`{data['requestor']}`", inline=False)
        youtube = Button(label="YouTube", url=data['url'], emoji="<:Eyt:1166437726732701827>")
        view = View()
        view.add_item(youtube)
        await ctx.send(embed=em, view=view)


    @commands.hybrid_command(name="skip", description="Skips a song.", usage="skip")
    @commands.guild_only()
    async def skip(self, ctx):
        if not await self.check_player(ctx):
            return
        if not ctx.voice_client.is_playing():
            await ctx.send(f"{self.bot.fail} | Player is not playing anything.")
        
        data = self.get_song(ctx.guild.id)
        ctx.voice_client.stop()
        em = discord.Embed(title="Skipped", description=f"[{data['title']}]({data['url']})", color=discord.Colour.dark_theme())
        em.set_footer(text=f"Skipped by: {ctx.author}")
        await ctx.send(embed=em)
    
    
    @commands.hybrid_command(name="stop", description="Stop playing and clear the queue.", usage="stop")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def stop(self, ctx):
        if not await self.check_player(ctx):
            return
        
        data = self.database[ctx.guild.id]['queue']
        if not data:
            await ctx.send(f"{self.bot.warning} | Queue is already empty.")
        self.delete_all(ctx.guild.id)
        await ctx.send(f"{self.bot.success} | Successfully stopped the player and cleared the queue.")
        ctx.voice_client.stop()
        
    
    
    @commands.hybrid_command(name="play", description="Plays a song.", aliases=["p"], usage="play <term>")
    @commands.guild_only()
    @app_commands.describe(term="Song name or url which you want to play.")
    async def play(self, ctx, *, term):
        if not ctx.author.voice:
            await ctx.send(f"{self.bot.fail} | You are not connected to any voice channel.")
            return
        if ctx.voice_client:
            if not ctx.voice_client.channel is ctx.author.voice.channel:
                await ctx.send(f"{self.bot.fail} | I am already connected to a voice channel.")
                return
        else:
            await ctx.author.voice.channel.connect(self_deaf=True)
            await ctx.send(f"{self.bot.success} | Successfully connected to `{ctx.author.voice.channel}`.")
        em = discord.Embed(title="Initialising the player", color=discord.Colour.dark_theme())
        message = await ctx.send(embed=em)
        term = term.strip("<>")
        self.setup_song(ctx, term)
        data = self.get_song(ctx.guild.id)
        
        em = discord.Embed(title="Searching", description=term, color=discord.Colour.dark_theme())
        message = await message.edit(embed=em)

        playing = ctx.voice_client.is_playing()
        
        rows = self.database[ctx.guild.id]['queue']
        data = rows[-1]
            
        em = discord.Embed(description=f"[{data['title']}]({data['url']})", color=discord.Colour.dark_theme())
        em.set_author(name="Added to queue" if playing else "Now playing", icon_url=ctx.me.display_avatar.url)
        em.set_thumbnail(url=data['thumbnail'])
        em.add_field(name="Channel", value=data['author'], inline=False)
        em.add_field(name="Duration", value=clean_time(data['duration']), inline=False)
        em.set_footer(text=f"Requested by: {ctx.author}")

        if playing:
            em.add_field(name="Queue number", value=len(rows)-1, inline=False)
            
        if not playing:
            source = await discord.FFmpegOpusAudio.from_probe(data['source'], **self.ffmpeg_options)
            ctx.voice_client.play(source, after= lambda c: self.after_playing(ctx))
        await message.edit(embed=em)
    
    
    
    @commands.hybrid_command(name="247", description="Toggles 24/7 music config.", usage="247")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def _247(self, ctx):
        if not await self.check_player(ctx):
            return

        async with aiosqlite.connect(self.configpath) as db:
            async with db.execute(f'''SELECT Voice FROM Configs WHERE Guild = {ctx.guild.id}''') as c:
                entry = await c.fetchone()
                vchannel = entry[0]
        
                if not vchannel:
                    await db.execute(f"""UPDATE Configs SET Voice = {ctx.voice_client.channel.id} WHERE Guild = {ctx.guild.id}""")
                    await ctx.send("<:Eonline:1137355060645466153> | Successfully enabled `24/7` mode.")
                else:
                    await db.execute(f"""UPDATE Configs SET Voice = 0 WHERE Guild = {ctx.guild.id}""")
                    await ctx.send("<:Ednd:1137355047752187944> | Successfully disabled `24/7` mode.")
            await db.commit()
    
    
    @commands.hybrid_command(name="loop", description="Toggles loop music config.", usage="loop")
    @commands.guild_only()
    async def loop(self, ctx):
        if not await self.check_player(ctx):
            return
        em = discord.Embed(title="Select a action", color=self.bot.color)
        em.set_image(url="https://cdn.discordapp.com/attachments/1165698279334481980/1166047193069793431/select_one.png")
        view = LoopButtons(ctx, self.database)
        view.message = await ctx.send(embed=em, view=view)

async def setup(bot):
    await bot.add_cog(Music(bot))