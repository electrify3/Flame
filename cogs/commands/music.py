import re

import discord
import lavalink

from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button

from lavalink.events import TrackStartEvent, QueueEndEvent
from lavalink.errors import ClientError
from lavalink.filters import LowPass
from lavalink.server import LoadType

from utils.tools import clean_time
from utils.paginator import Paginator

url_rx = re.compile(r'https?://(?:www\.)?.+')


class LoopButtons(View):
    def __init__(self, ctx, player: lavalink.DefaultPlayer):
        super().__init__(
        timeout = 30
        )
        self.ctx = ctx
        self.player = player
        self.message: discord.Message = None
    
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
        loop = self.player.loop
        if loop == 1:
            self.player.set_loop(0)
            await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled `song loop` mode.", embed=None, view=None)
        else:
            self.player.set_loop(1)
            await self.message.edit(content="<:Eonline:1137355060645466153> | Successfully enabled `song loop` mode.", embed=None, view=None)
        self.stop()
    
    
    @discord.ui.button(label='Playlist Loop', emoji="🔂", style=discord.ButtonStyle.blurple)
    async def playlistloop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        loop = self.player.loop
        if loop == 2:
            self.player.set_loop(0)
            await self.message.edit(content="<:Ednd:1137355047752187944> | Successfully disabled `playlist loop` mode.", embed=None, view=None)
        else:
            self.player.set_loop(2)
            await self.message.edit(content="<:Eonline:1137355060645466153> | Successfully enabled `playlist loop` mode.", embed=None, view=None)
        self.stop()




class Controller(Paginator):
    def __init__(self, ctx, items, page, max_pages):
        super().__init__(ctx, items, page, max_pages)

    def make_page(self):
        description = "\n".join(data for data in self.items[self.page*10-10:self.page*10])
        embed = discord.Embed(title="Current Queue", description=description[:4000], color=discord.Colour.dark_theme())
        embed.set_author(name=self.ctx.me, icon_url=self.ctx.me.display_avatar.url)
        embed.set_footer(text=f"Page {self.page}/{self.max_pages}")
        return embed


class LavalinkVoiceClient(discord.VoiceProtocol):
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = channel.guild.id
        self._destroyed = False

        if not hasattr(self.client, 'lavalink'):
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(host='localhost', port=8080, password='password',
                                          region='us', name='default-node')

        self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        channel_id = data['channel_id']

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }

        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_deaf=True, self_mute=self_mute)

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if not force and not player.is_connected:
            return

        await self.channel.guild.change_voice_state(channel=None)

        player.channel_id = None
        await self._destroy()

    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            return

        self._destroyed = True

        try:
            await self.lavalink.player_manager.destroy(self.guild_id)
        except ClientError:
            pass


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = "<:Emusic:1165576153235460117>"
        self.current: dict[int, lavalink.AudioTrack] = {}
        self.played: dict[int, set[str]] = {}


        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(host='localhost', port=8080, password='password',
                                  region='us', name='default-node')

        self.lavalink: lavalink.Client = bot.lavalink
        self.lavalink.add_event_hooks(self)


    
    async def create_player(ctx: commands.Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        player = ctx.bot.lavalink.player_manager.create(ctx.guild.id)
        should_connect = ctx.command.name in ('play',)


        voice_client = ctx.voice_client

        if not ctx.author.voice or not ctx.author.voice.channel:
            if voice_client is not None:
                raise commands.CommandInvokeError('You need to join my voice channel first.')

            raise commands.CommandInvokeError('Join a voicechannel first.')

        voice_channel = ctx.author.voice.channel

        if voice_client is None:
            if not should_connect:
                raise commands.CommandInvokeError("I'm not playing music.")

            permissions = voice_channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            if voice_channel.user_limit > 0:
                if len(voice_channel.members) >= voice_channel.user_limit and not ctx.me.guild_permissions.move_members:
                    raise commands.CommandInvokeError('Your voice channel is full!')

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        elif voice_client.channel.id != voice_channel.id:
            raise commands.CommandInvokeError('You need to be in my voicechannel.')

        return True

    @lavalink.listener(TrackStartEvent)
    async def on_track_start(self, event: TrackStartEvent) -> None:
        guild_id = event.player.guild_id
        channel_id = event.player.fetch('channel')
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return await self.lavalink.player_manager.destroy(guild_id)

        channel = guild.get_channel(channel_id)

        if channel:
            track = event.track
            em = discord.Embed(description=f"[{track.title}]({track.uri})", color=discord.Colour.dark_theme())
            em.set_author(name="Now playing", icon_url=self.bot.user.display_avatar.url)
            em.set_thumbnail(url=track.artwork_url)
            em.add_field(name="Channel", value = track.author, inline = False)
            em.add_field(name="Duration", value = clean_time(track.duration//1000), inline = False)
            em.set_footer(text=f"Requested by: {track.requester}")
            await channel.send(embed=em)
        self.current[guild_id] = track
        self.played[guild_id].add(track.identifier)

    @lavalink.listener(QueueEndEvent)
    async def on_queue_end(self, event: QueueEndEvent) -> None:
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)

        if guild is not None:
            track: lavalink.AudioTrack = self.current[guild_id] 
            query = f"https://www.youtube.com/watch?v={track.identifier}&list=RD{track.identifier}"
            results = await event.player.node.get_tracks(query)
            tracks = []
            if results.load_type == LoadType.EMPTY:
                self.current[guild_id] = None
                return
            
            elif results.load_type == LoadType.PLAYLIST:
                tracks = results.tracks

            played = self.played[guild_id]
            for track in tracks:
                if track.identifier not in played:
                    break
            if track.identifier not in played:
                track.extra["requester"] = self.bot.user
                event.player.add(track=track)
                self.current[guild_id] = track
                await event.player.play()
                self.played[guild_id].add(track.identifier)


    @commands.hybrid_command(name="play", description="Plays a song or Playlist.", aliases=["p"], usage="play <query>")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(query="Song name or url which you want to play.")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        await ctx.defer()
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if ctx.guild.id not in self.played:
            self.played[ctx.guild.id] = set()

        query = query.strip('<>')
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)

        if results.load_type == LoadType.EMPTY:
            await ctx.send("I couldn'\t find any tracks for that query.")
            return
        
        elif results.load_type == LoadType.PLAYLIST:
            tracks = results.tracks

            for track in tracks:
                track.extra["requester"] = ctx.author
                player.add(track=track)
            em = discord.Embed(description=f'[{results.playlist_info.name}]({query}) - {len(tracks)} tracks', color=self.bot.color)
            em.set_author(name="Playlit Enqueued", icon_url=ctx.me.display_avatar.url)
            em.set_footer(text=f"Requested by: {ctx.author}")
            await ctx.send(embed=em)
        else:
            track = results.tracks[0]
            track.extra["requester"] = ctx.author
            player.add(track=track)

            if player.is_playing:
                em = discord.Embed(description=f"[{track.title}]({track.uri})", color=discord.Colour.dark_theme())
                em.set_author(name="Track Enqueued", icon_url=ctx.me.display_avatar.url)
                em.set_thumbnail(url=track.artwork_url)
                em.add_field(name="Channel", value = track.author, inline = False)
                em.add_field(name="Duration", value = clean_time(track.duration//1000), inline = False)
                em.set_footer(text=f"Requested by: {ctx.author}")
                await ctx.send(embed=em)

        if not player.is_playing:
            await player.play()


    @commands.hybrid_command(name="disconnect", description="Leaves the voice channel.", aliases=["dc", "leave"], usage="disconnect")
    @commands.guild_only()
    @commands.check(create_player)
    @commands.has_guild_permissions(move_members=True)
    async def disconnect(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send(f'{self.bot.success} | Successfully left the vc and destroyed the player.')


    @commands.hybrid_command(name="skip", description="Skips current song or removes a song from the queue.", aliases=['remove'], usage="skip [position]")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(position="Song position in queue")
    async def skip(self, ctx: commands.Context, position: int = 0):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player or not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        if not position:
            track: lavalink.AudioTrack = player.current
            await player.skip()
            em = discord.Embed(title="Skipped", description=f"[{track.title}]({track.uri})", color=discord.Colour.dark_theme())
            em.set_footer(text=f"Skipped by: {ctx.author}")
            await ctx.send(embed=em)
        else:
            songs: list[lavalink.AudioTrack] = player.queue

            if position > len(songs):
                return await ctx.send(f"{self.bot.fail} | No song found with id `{position}`.")
            
            track = songs[position-1]
            songs.pop(position-1)
            em = discord.Embed(title="Removed", description=f"[{track.title}]({track.uri})", color=discord.Colour.dark_theme())
            em.set_footer(text=f"Removed by: {ctx.author}")
            await ctx.send(embed=em)

    
    @commands.command(name="nowplaying", description="Display the current playing song.", aliases=["np"], usage="nowplaying")
    @commands.check(create_player)
    async def nowplaying(self, ctx):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        track: lavalink.AudioTrack = player.current
        em = discord.Embed(title="Now Playing", description=f"[{track.title}]({track.uri})", color=discord.Colour.dark_theme())
        em.set_author(name=ctx.me, icon_url=ctx.me.display_avatar.url)
        em.set_image(url=track.artwork_url)
        em.add_field(name="Channel", value=track.author, inline=False)
        em.add_field(name="Duration", value = clean_time(track.duration//1000), inline=False)
        em.add_field(name="Paused", value=f'{player.paused}')
        em.add_field(name="Requestor", value=f"`{track.requester}`", inline=False)
        youtube = Button(label="YouTube", url=track.uri, emoji="<:Eyt:1166437726732701827>")
        view = View()
        view.add_item(youtube)
        await ctx.send(embed=em, view=view)


    @commands.hybrid_command(name="queue", description="Shows the current queue.", aliases=["q"], usage="queue [page]")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(page="page no.")
    async def queue(self, ctx, page: int = 1):
        player: lavalink.player.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        songs: list[lavalink.AudioTrack] = player.queue
        data = []
        
        max_pages = len(songs)//10
        if max_pages <= len(songs)/10:
            max_pages += 1
            
        if page < 0 or page > max_pages or not songs:
            em = discord.Embed(title="Queue Empty", description="No song in the queue.", color=discord.Colour.red())
            await ctx.send(embed=em)
            return

        data.append(f"<:Eonline:1137355060645466153> Now Playing: [{player.current.title}]({player.current.uri}) - `{player.current.requester}`\n")
        for index, song in enumerate(songs, start=1):
            data.append(f"{index}. [{song.title}]({song.uri}) - `{song.requester}`\n")
            
        view = Controller(ctx, data, page, max_pages)
        em = view.make_page()
        view.set_view()
        view.message = await ctx.send(embed=em, view=view)


    @commands.hybrid_command(name="volume", description="Changes the volume.", aliases=["vol"], usage="volume [value]")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(value="Volume value")
    async def volume(self, ctx: commands.Context, value: int = None):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        if value is None:
            return await ctx.send(f'<:Evoice:1127301699506274425> | Current volume: {player.volume}.')
        
        if value < 0 or value > 1000:
            return await ctx.reply(f"{self.bot.warning} | Volume can't be more then 1000 and less then 0.", delete_after=5)
        
        await player.set_volume(value)
        await ctx.send(f'{self.bot.success} | Successfully set volume to {value}.')


    @commands.hybrid_command(name="speed", description="Changes the speed.", usage="speed [value]")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(value="Speed value")
    async def speed(self, ctx: commands.Context, value: float = None):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        timescale = player.get_filter('timescale')
        filter = timescale if timescale is not None else lavalink.filters.Timescale()
        speed = filter.serialize()['timescale'].get('speed')

        if value is None:
            if speed:
                return await ctx.send(f'<:Edoublearrow:1180723248388902933> | Current speed: {speed}x.')
            else:
                return await ctx.send(f'<:Edoublearrow:1180723248388902933> | Current speed: 1x.')

        if value < 0.1 or value > 3:
            return await ctx.reply(f"{self.bot.warning} | Speed can't be more then 5x and less then 0.1x.", delete_after=5)
        
        filter.update(speed=value)

        await player.set_filter(filter)
        await ctx.send(f'{self.bot.success} | Successfully set speed to {value}x.')


    @commands.hybrid_command(name="pitch", description="Changes the pitch.", usage="pitch [value]")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(value="Pitch value")
    async def pitch(self, ctx: commands.Context, value: float = None):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        timescale = player.get_filter('timescale')
        filter = timescale if timescale is not None else lavalink.filters.Timescale()
        pitch = filter.serialize()['timescale'].get('pitch')

        if value is None:
            if pitch:
                return await ctx.send(f'<:Eonline:1137355060645466153> | Current pitch: {pitch}x.')
            else:
                return await ctx.send(f'<:Eonline:1137355060645466153> | Current pitch: 1x.')

        if value < 0.1 or value > 3:
            return await ctx.reply(f"{self.bot.warning} | Pitch can't be more then 5x and less then 0.1x.", delete_after=5)
        
        filter.update(pitch=value)

        await player.set_filter(filter)
        await ctx.send(f'{self.bot.success} | Successfully set pitch to {value}x.')


    @commands.hybrid_command(name="rate", description="Changes the music rate.", usage="rate [value]")
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(value="Rate value")
    async def rate(self, ctx: commands.Context, value: float = None):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        timescale = player.get_filter('timescale')
        filter = timescale if timescale is not None else lavalink.filters.Timescale()
        rate = filter.serialize()['timescale'].get('rate')

        if value is None:
            if rate:
                return await ctx.send(f'<:Eonline:1137355060645466153> | Current rate: {rate}x.')
            else:
                return await ctx.send(f'<:Eonline:1137355060645466153> | Current rate: 1x.')

        if value < 0.1 or value > 3:
            return await ctx.reply(f"{self.bot.warning} | Rate can't be more then 5x and less then 0.1x.", delete_after=5)
        
        filter.update(rate=value)

        await player.set_filter(filter)
        await ctx.send(f'{self.bot.success} | Successfully set rate to {value}x.')




    @commands.hybrid_command(name='pause', description='Pauses the player', usage='pause')
    @commands.guild_only()
    @commands.check(create_player)
    async def pause(self, ctx: commands.Context):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.paused:
            return await ctx.send(f"{self.bot.warning} | Player is already paused, use `{ctx.prefix}resume` to resume the player.")
        elif not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        await player.set_pause(pause=True)
        await ctx.send(f'{self.bot.success} | Paused the player.')


    @commands.hybrid_command(name='resume', description='Resumes the player', usage='resume')
    @commands.guild_only()
    @commands.check(create_player)
    async def resume(self, ctx: commands.Context):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.paused and player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Player is not paused!")
        elif not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        await player.set_pause(pause=False)
        await ctx.send(f'{self.bot.success} | Resumed the player.')
    

    @commands.hybrid_command(name="stop", description="Stops the player and clear the queue.", usage="stop")
    @commands.guild_only()
    @commands.check(create_player)
    @commands.has_guild_permissions(moderate_members=True)
    async def stop(self, ctx: commands.Context) -> None:
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")

        player.queue.clear()
        await player.stop()
        await ctx.send(f'{self.bot.success} | Successfully stopped the player and cleared the queue.')


    @commands.hybrid_command(name='loop', description='Configures bot\'s loop settings.', usage='loop')
    @commands.guild_only()
    @commands.check(create_player)
    async def loop(self, ctx: commands.Context):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        em = discord.Embed(title="Select a action", color=self.bot.color)
        em.set_image(url="https://cdn.discordapp.com/attachments/1165698279334481980/1166047193069793431/select_one.png")
        view = LoopButtons(ctx, player)
        view.message = await ctx.send(embed=em, view=view)


    @commands.hybrid_command(name='seek', description='Set the track at certain position.', usage='seek <position:sec>')
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(position='Song position in seconds.')
    async def seek(self, ctx: commands.Context, position: int):
        player: lavalink.DefaultPlayer = self.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        position_mili = position*1000
        track_length = player.current.duration
        
        if position_mili < 0 or position_mili > track_length:
            return await ctx.send(f"{self.bot.warning} | Position can't be less then 0 or more then {track_length//1000}.")
        
        await player.seek(position_mili)
        await ctx.send(f'{self.bot.success} | Track is now set at position {clean_time(position)}.')

    

    @commands.hybrid_command(name='position', description='Tells the current position of the track.', aliases=['pos'], usage='position')
    @commands.guild_only()
    @commands.check(create_player)
    async def position(self, ctx: commands.Context):
        player: lavalink.DefaultPlayer = self.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{self.bot.warning} | Currently no song is playing.")
        
        track_length = player.current.duration//1000
        position = player.position//1000
        
        await ctx.send(f'<:Eping:1138002794197041223> | Current position of the track is: {clean_time(position)}/{clean_time(track_length)} | in secs: {position}/{track_length} [{((position/track_length)*100):.1f}%]')




    
    
    @commands.hybrid_command(name='lowpass', description='Set lowpass filter', aliases=['lp'], usage='lowpass <strength>')
    @commands.guild_only()
    @commands.check(create_player)
    @app_commands.describe(strength="Filter stength")
    async def lowpass(self, ctx: commands.Context, strength: float):
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        strength = max(0.0, strength)
        strength = min(100, strength)

        if strength == 0.0:
            await player.remove_filter('lowpass')
            return await ctx.send(f'{self.bot.success} | Successfully disabled Low Pass Filter.')

        low_pass = LowPass()
        low_pass.update(smoothing=strength)

        await player.set_filter(low_pass)
        await ctx.send(f'{self.bot.success} | Successfully set Low Pass Filter strength to {strength}.')

async def setup(bot):
    await bot.add_cog(Music(bot))