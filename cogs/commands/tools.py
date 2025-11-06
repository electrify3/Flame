import io
import re
import typing

import discord
import requests

from discord import app_commands
from discord.ui import View
from discord.ext import commands

from utils import tools

class ResetChannel(View):
    def __init__(self, ctx):
        super().__init__(
        timeout = 30
        )
        self.ctx = ctx
        self.message = None
    
    async def on_timeout(self):
        await self.message.edit(content=f"{self.ctx.bot.fail} | No confirmation found in last 30seconds.", view=None)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            return False
        else:
            return True
    
    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        channel = await self.ctx.channel.clone(reason=f"{self.ctx.author} used nuke command.")
        await channel.edit(position=self.ctx.channel.position, reason="{self.ctx.author} used nuke command.")
        await self.ctx.channel.delete()
        await channel.send(f"{interaction.client.success} | `{self.ctx.author}` successfully nuked `{self.ctx.channel.name}`.")
        await channel.send("https://tenor.com/view/oppenheimer-walking-through-the-press-with-their-cameras-oppenheimer-oppenheimer-movie-j-robert-oppenheimer-robert-oppenheimer-gif-3805440999848096280")
        self.stop()
    
    @discord.ui.button(label='Abort', style=discord.ButtonStyle.red)
    async def abort(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()
        self.stop()
        

class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages = {}
        self.emoji = "<:Eutility:1127303124634325002>"
    
    
    @commands.Cog.listener("on_message_delete")
    async def save_message(self, message):
        if message.author.bot: return
        self.sniped_messages[str(message.channel.id)] = message
    
    
    @commands.hybrid_command(name="embed", description="Sends an embed to a selected channel.", usage="embed <channel/id> <title> [description]", aliases=["em"])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @app_commands.describe(channel="Channel where you want to send embed.", description="Content of your embed.", title="Title of your embed.")
    async def embed(self, ctx, channel: discord.TextChannel, *, title, description=None):
        await ctx.defer()
        em = discord.Embed(title=title, description=description, color=self.bot.color)
        await channel.send(embed=em)
        await ctx.send (f'{self.bot.success} | embed was sent to **{channel.mention}**.')
    
    @commands.hybrid_command(name="snipe", description="Shows the latest deleted message of the channel", usage="snipe")
    @commands.guild_only()
    async def snipe(self, ctx):
        message = self.sniped_messages.get(str(ctx.channel.id))
        if not message:
            return await ctx.send(f"{self.bot.fail} | No recently deleted message found.")
        em = discord.Embed(title="Deleted Message Snipe", description=message.content or "**[No text found in deleted message]**", timestamp=message.created_at, color=self.bot.color)
        em.add_field(name="Author", value=message.author, inline=False)
        em.set_thumbnail(url=message.author.display_avatar.url)
        if message.attachments:
            em.set_image(url=message.attachments[0].proxy_url)
        elif message.stickers:
            em.set_image(url=message.stickers[0].url)
        em.set_footer(text=f"Requested by: {ctx.author}")
        await ctx.send(embed=em)
        
    
    @commands.hybrid_command(name="channelname", description="Change a channel name.", aliases=["cn"], usage="channelname <channel/id> <new name>")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    @app_commands.describe(channel="Channel who's name you want to change.")
    async def channelname(self, ctx, channel: typing.Optional[discord.TextChannel], *, name):
        if not channel: channel = ctx.channel
        text = f"{self.bot.success} | Successfully changed `{channel}` name to `{name}`."
        await channel.edit(name=name, reason=f"{ctx.author} used channelname.")
        await ctx.send(text)
    
    
    @commands.hybrid_command(name="nuke", description="Nukes this channel.", usage="nuke")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def nuke(self, ctx):
        view = ResetChannel(ctx)
        view.message = await ctx.send(f"{self.bot.warning} | {ctx.author.mention} are you sure you want to nuke {ctx.channel.mention}.", view=view)
    
    
    @commands.hybrid_command(name="slowmode", description="Set slowmode for current channel.", usage="slowmode <time/off>")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    @app_commands.describe(duration="Time for slowmode eg. 1hr30m15s or None.")
    async def slowmode(self, ctx, duration):
        await ctx.defer()
        if duration.lower() in ["0", "off", "disable", "none"]:
            await ctx.channel.edit(slowmode_delay=0)
            em = discord.Embed(title="Success", description="I turned off slowmode.", color=self.bot.color)
            em.add_field(name="Channel", value=ctx.channel.mention, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
            await ctx.send(embed=em)
            return
        duration = tools.format_time(duration)
        
        if duration.total_seconds() == 0:
            em = discord.Embed(title="Error!", description="Invalid time format.", color=discord.Colour.red())
            em.add_field(name="Syntax", value=f"`{ctx.prefix}slowmode 1h30m15s | None`.", inline = False)
            await ctx.send(embed=em)
            return
        
        if duration.total_seconds() > 21600 :
            em = discord.Embed(title="Error!", description="Slowmode can't be more than 6hrs.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        
        await ctx.channel.edit(slowmode_delay=duration.total_seconds(), reason=f"{ctx.author} used slowmode.")
        em = discord.Embed(title="Success", description="I turned on slowmode.", color=self.bot.color)
        em.add_field(name="Channel", value=ctx.channel.mention, inline = False)
        em.add_field(name="Duration", value=duration, inline = False)
        em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
        
        await ctx.send(embed=em)
    
    @commands.hybrid_command(name="lockdown", description="Locks a channel.", aliases=["lock"], usage="lockdown [channel/id] [role]")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    @app_commands.describe(channel="Channel you want to lock.", role="Role you want to unlock.")
    async def lockdown(self, ctx, channel: typing.Optional[discord.TextChannel], *, role: typing.Optional[str]):
        if not channel: channel = ctx.channel
        if role:
            name = role
            role = tools.find_role(ctx, role)
            if not role:
                return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            overwrite = channel.overwrites_for(role)
            if overwrite.send_messages is False:
                em = discord.Embed(title="Failed", description=f"{channel.mention} is already locked for {role.mention}.", color = discord.Colour.red())
                return await ctx.send(embed=em)
                
            overwrite.send_messages = False
            await channel.set_permissions(role, overwrite = overwrite, reason=f"{ctx.author} used lockdown.")
        
            em = discord.Embed(title="Success", description=f"I successfully locked {channel.mention} for {role.mention}.", color = self.bot.color)
            return await ctx.send(embed=em)
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        if overwrite.send_messages is False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is already locked.", color = discord.Colour.red())
            return await ctx.send(embed=em)
        
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used lockdown.")
        
        em = discord.Embed(title="Success", description=f"I successfully locked {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    
    @commands.hybrid_command(name="unlockdown", description="Unlocks a channel.", aliases=["unlock"], usage="unlockdown [channel/id] [role]")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    @app_commands.describe(channel="Channel you want to unlock.", role="Role you want to unlock.")
    async def unlockdown(self, ctx, channel: typing.Optional[discord.TextChannel], *, role: typing.Optional[str]):
        if not channel: channel = ctx.channel
        if role:
            name = role
            role = tools.find_role(ctx, role)
            if not role: return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            overwrite = channel.overwrites_for(role)
            if overwrite.send_messages is not False:
                em = discord.Embed(title="Failed", description=f"{channel.mention} is already unlocked for {role.mention}.", color = discord.Colour.red())
                return await ctx.send(embed=em)
            overwrite.send_messages = None
            await channel.set_permissions(role, overwrite = overwrite, reason=f"{ctx.author} used unlock.")
            
            em = discord.Embed(title="Success", description=f"I successfully unlocked {channel.mention} for {role.mention}.", color = self.bot.color)
            return await ctx.send(embed=em)
        
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        if overwrite.send_messages is not False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is already unlocked.", color = discord.Colour.red())
            return await ctx.send(embed=em)
        
        overwrite.send_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used unlock.")
        
        em = discord.Embed(title="Success", description=f"I successfully unlocked {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    @commands.hybrid_command(name="hide", description="Hides a channel.", usage="hide [channel/id] [role]")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    @app_commands.describe(channel="Channel you want to hide.", role="Role you want to hide.")
    async def hide(self, ctx, channel: typing.Optional[discord.TextChannel], *, role: typing.Optional[str]):
        if not channel: channel = ctx.channel
        if role:
            name = role
            role = tools.find_role(ctx, role)
            if not role: return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            overwrite = channel.overwrites_for(role)
            if overwrite.view_channel is False:
                em = discord.Embed(title="Failed", description=f"{channel.mention} is already hidden for {role.mention}.", color = discord.Colour.red())
                return await ctx.send(embed=em)
            overwrite.view_channel = False
            await channel.set_permissions(role, overwrite = overwrite, reason=f"{ctx.author} used hide.")
            em = discord.Embed(title="Success", description=f"I successfully hided {channel.mention} for {role.mention}.", color = self.bot.color)
            return await ctx.send(embed=em)
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        if overwrite.view_channel is False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is already hidden.", color = discord.Colour.red())
            return await ctx.send(embed=em)
        
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used hide.")
        
        em = discord.Embed(title="Success", description=f"I successfully hided {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    @commands.hybrid_command(name="unhide", description="Unhides a channel.", usage="unhide [channel/id] [role]")
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    @app_commands.describe(channel="Channel you want to unhide.", role="Role you want to unhide.")
    async def unhide(self, ctx, channel: typing.Optional[discord.TextChannel], *, role: typing.Optional[str]):
        if not channel: channel = ctx.channel
        if role:
            name = role
            role = tools.find_role(ctx, role)
            if not role: return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            overwrite = channel.overwrites_for(role)
            if overwrite.view_channel is not False:
                em = discord.Embed(title="Failed", description=f"{channel.mention} is not hidden for {role.mention}.", color = discord.Colour.red())
                return await ctx.send(embed=em)
            
            overwrite.view_channel = None
            await channel.set_permissions(role, overwrite = overwrite, reason=f"{ctx.author} used unhide.")
            
            em = discord.Embed(title="Success", description=f"I successfully unhided {channel.mention} for {role.mention}.", color = self.bot.color)
            return await ctx.send(embed=em)
        
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        
        if overwrite.view_channel is not False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is not hidden.", color = discord.Colour.red())
            return await ctx.send(embed=em)
        
        overwrite.view_channel = None
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used unhide.")
        
        em = discord.Embed(title="Success", description=f"I successfully unhided {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    
    
    @commands.hybrid_command(name="nickname", description="Changes nickname of a member.", aliases=["nick", "setnick", "name"], usage="nickname <user/id> <new name>")
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    @app_commands.describe(members="Member(s) whose nickname you want to change.", name="Name you want to set.")
    async def nickname(self, ctx, members: commands.Greedy[discord.Member],*, name=None):
        members = [*set(members)]
        for member in members:
            try:
                await member.edit(nick=name, reason=f"{ctx.author} used nickname.")
                await ctx.send(f"{self.bot.success} | Successfully changed `{member}`'s nickname to `{name}`.")
            except :
                await ctx.send(f"{self.bot.fail} | I am unable to change `{member}`'s nickname.")
    
    
    
    @commands.hybrid_command(name="steal", description="Add emojis from a link or emoji itself.", usage="steal [emoji|link|reply]", aliases=["emoji"])
    @commands.has_permissions(manage_emojis=True)
    @commands.guild_only()
    @app_commands.describe(input="Emoji or link.")
    async def steal(self, ctx, input: commands.Greedy[typing.Union[discord.PartialEmoji, str]] = None):
        
        if input:
            input = [element for element in input if str(element).strip("<>").startswith("https://") or isinstance(element, discord.PartialEmoji)]
        if not input:
            if ctx.message.reference:
                message = await ctx.fetch_message(ctx.message.reference.message_id)
                raw_input = message.content.split()
                urls = [element for element in raw_input if element.strip("<>").startswith("https://")]
                emotes = [discord.PartialEmoji.from_str(element) for element in raw_input if re.match(r'<(a?):([a-zA-Z0-9\_]+):([0-9]+)>$', element)]
                input = urls + emotes
        input = [*set(input)]
        if not input:
            await ctx.send(f"{self.bot.fail} | Failed, no `emoji/link` was found.")
            return
        for element in input:
            if isinstance(element, discord.PartialEmoji):
                element._state = self.bot._connection
                image = await element.read()
                try:
                    emoji = await ctx.guild.create_custom_emoji(name=element.name, image=image, reason=f"{ctx.author} used steal command.")
                    await ctx.send(f"{self.bot.success} | Successfully added a emoji {emoji}.")
                except: await ctx.send(f"{self.bot.fail} | Failed, You may check asset size or server emoji slots.")
                    
            elif str(element).startswith("https://"):
                name = f"emoji_{len(ctx.guild.emojis)+1}"
                image = requests.get(element).content
                try:
                    emoji = await ctx.guild.create_custom_emoji(name=name, image=image, reason=f"{ctx.author} used steal command.")
                    await ctx.send(f"{self.bot.success} | Successfully added a emoji {emoji}.")
                except: await ctx.send(f"{self.bot.fail} | Failed, You may check asset size or server emoji slots.")
    
    
    @commands.hybrid_command(name="sticker", description="Adds a sticker from a url, emoji or a sticker.", aliases=["ss", "steals", "stealsticker"], usage="sticker <input>")
    @commands.has_permissions(manage_emojis=True)
    @commands.guild_only()
    @app_commands.describe(input="Emoji, url or sticker you want to add as sticker.")
    async def sticker(self, ctx, input: commands.Greedy[typing.Union[discord.PartialEmoji, str]] = None):
        if input: input = input[0]
        if input and not (str(input).strip("<>").startswith("https://") or isinstance(input, discord.PartialEmoji)): input = None
        if not input and ctx.message.stickers: input = ctx.message.stickers[0]
        elif ctx.message.reference:
            message = await ctx.fetch_message(ctx.message.reference.message_id)
            if message.stickers: input = message.stickers[0]
            else:
                urls = [element for element in message.content.split(" ") if element.strip("<>").startswith("https://")]
                emotes = [discord.PartialEmoji.from_str(element) for element in message.content.split() if re.match(r'<(a?):([a-zA-Z0-9\_]+):([0-9]+)>$', element)]
                if not (urls + emotes): input = None
                else: input = (urls + emotes)[0]
        if not input:
            await ctx.send(f"{self.bot.fail} | Failed, no `emoji/link/sticker` was found.")
            return
        
        if str(input).strip("<>").startswith("https://"):
            name = f"sticker_{len(ctx.guild.stickers)+1}"
            image = io.BytesIO(requests.get(input).content)
            file = discord.File(fp=image)
            try:
                sticker = await ctx.guild.create_sticker(name=name, file=file, emoji="🤖", description=f"Added by {ctx.author}.", reason=f"{ctx.author} used sticker command.")
                await ctx.send(f"{self.bot.success} | Successfully added a sticker.", stickers=[sticker])
            except: await ctx.send(f"{self.bot.fail} | Failed, You may check asset size/type or server sticker slots.")
        elif isinstance(input, discord.PartialEmoji):
            input._state = self.bot._connection
            file = await input.to_file()
            try:
                sticker = await ctx.guild.create_sticker(name=input.name, file=file, description=f"Added by {ctx.author}.", emoji="🤖", reason=f"{ctx.author} used sticker command.")
                await ctx.send(f"{self.bot.success} | Successfully added a sticker.", stickers=[sticker])
            except: await ctx.send(f"{self.bot.fail} | Failed, You may check asset size/type or server sticker slots.")
        elif isinstance(input, discord.StickerItem):
            data = await input.fetch()
            image = io.BytesIO(requests.get(input.url).content)
            file = discord.File(fp=image)
            try:
                sticker = await ctx.guild.create_sticker(name=data.name, file=file, description=data.description, emoji=data.emoji, reason=f"{ctx.author} used sticker command.")
                await ctx.send(f"{self.bot.success} | Successfully added a sticker.", stickers=[sticker])
            except: await ctx.send(f"{self.bot.fail} | Failed, You may check asset size/type or server sticker slots.")
    
    
    @commands.hybrid_command(name="afk", description="Set afk for you.", usage="afk [message]")
    @commands.guild_only()
    @app_commands.describe(message="Your afk message.")
    async def afk(self, ctx, *, message:str = "No message provided."):
        await ctx.defer(ephemeral=True)
        tools.setup_afk(ctx.author)
        tools.add_afk(ctx.author, message)
        await ctx.send(f"**{ctx.author.mention}, Alright I'll manage it, Enjoy yourself {ctx.author}.**", delete_after=3)
    

async def setup(bot):
    await bot.add_cog(Tools(bot))