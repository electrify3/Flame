import discord

from discord import app_commands
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Evoice:1127301699506274425>"
    
    @commands.hybrid_group(name="voice", description="This is the base command of all other voice commands.", usage="voice <command>", aliases=["v"])
    @commands.guild_only()
    async def voice(self, ctx):
        return
    
    
    @voice.command(name="lock", description="Locks a voice channel.", usage="voice lock [voice-channel]")
    @app_commands.describe(channel="The channel you want to lock.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.VoiceChannel):
        await ctx.defer()
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.connect is False and overwrite.send_messages is False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is already locked. \n\nIf members are still able to connect, you may check `role/user` overwrites.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        overwrite.connect = False
        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used voice lock command.")
        
        em = discord.Embed(title="Success", description=f"I successfully locked {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    
    @voice.command(name="unlock", description="Unlocks a voice channel.", usage="voice unlock [voice-channel]")
    @app_commands.describe(channel="The channel you want to unlock.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.VoiceChannel):
        await ctx.defer()
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.connect is not False and overwrite.send_messages is not False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is not locked. \n\nIf members are still not able to connect, you may check `role/user` overwrites.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        overwrite.connect = None
        overwrite.send_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used voice lock command.")
        em = discord.Embed(title="Success", description=f"I successfully unlocked {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    
    
    @voice.command(name="hide", description="Hides a voice channel.", usage="voice hide [voice-channel]")
    @commands.has_permissions(manage_channels=True)
    @app_commands.describe(channel="Channel you want to hide.")
    async def hide(self, ctx, channel: discord.VoiceChannel):
        await ctx.defer()
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.view_channel is False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is already hidden. \n\nIf members are still able to see it, you may check `role/user` overwrites.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        overwrite.view_channel = False
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used voice hide command.")
        
        em = discord.Embed(title="Success", description=f"I successfully hided {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    
    @voice.command(name="unhide", description="Unhides a voice channel.", usage="voice unhide [voice-channel]")
    @commands.has_permissions(manage_channels=True)
    @app_commands.describe(channel="Channel you want to unhide.")
    async def unhide(self, ctx, channel: discord.VoiceChannel):
        await ctx.defer()
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.view_channel is not False:
            em = discord.Embed(title="Failed", description=f"{channel.mention} is not hidden. \n\nIf members are still able to connect, you may check `role/user` overwrites.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        overwrite.view_channel = None
        await channel.set_permissions(ctx.guild.default_role, overwrite = overwrite, reason=f"{ctx.author} used voice unhide command.")
        em = discord.Embed(title="Success", description=f"I successfully unhided {channel.mention}.", color = self.bot.color)
        await ctx.send(embed=em)
    
    
    
    @voice.command(name="kick", description="Disconnect's a user(s) from a voice channel.", usage="voice kick <@members/ids>")
    @commands.has_guild_permissions(move_members=True)
    @app_commands.describe(members="Members you want to disconnect.")
    async def kick(self, ctx, members: commands.Greedy[discord.Member]):
        await ctx.defer()
        if not members:
            await ctx.send(f"{self.bot.warning} | Provide atleast one @member/id.")
            return
        for member in members:
            if not member.voice:
                await ctx.send(f"{self.bot.fail} | `{member}` not in voice channel.")
                continue
            await member.move_to(None, reason=f"{member}: Used voice kick command.")
            await ctx.send(f"{self.bot.success} | Successfully voice kicked `{member}`.")
    
    
    @voice.command(name="mute", description="Voice mutes a member.", usage="voice mute <@members/ids>")
    @commands.has_guild_permissions(mute_members=True)
    @app_commands.describe(members="Members you want to voice mute.")
    async def mute(self, ctx, members: commands.Greedy[discord.Member]):
        await ctx.defer()
        if not members:
            await ctx.send(f"{self.bot.warning} | Provide atleast one @member/id.")
            return
        for member in members:
            if not member.voice:
                await ctx.send(f"{self.bot.fail} | `{member}` not in voice channel.")
                continue
            if member.voice.mute:
                await ctx.send(f"{self.bot.fail} | `{member}` is already voice muted.")
                continue
            await member.edit(mute=True, reason=f"{member}: Used voice mute command.")
            await ctx.send(f"{self.bot.success} | Successfully voice muted `{member}`.")
    
    
    
    @voice.command(name="unmute", description="Voiceunmutes a member.", usage="voice unmute <@members/ids>")
    @commands.has_guild_permissions(mute_members=True)
    @app_commands.describe(members="Members you want to voice ummute.")
    async def voiceunmute(self, ctx, members: commands.Greedy[discord.Member]):
        await ctx.defer()
        if not members:
            await ctx.send(f"{self.bot.warning} | Provide atleast one @member/id.")
            return
        for member in members:
            if not member.voice:
                await ctx.send(f"{self.bot.fail} | `{member}` not in voice channel.")
                continue
            if not member.voice.mute:
                await ctx.send(f"{self.bot.fail} | `{member}` is not voice muted.")
                continue
            await member.edit(mute=False, reason=f"{member}: Used voice unmute command.")
            await ctx.send(f"{self.bot.success} | Successfully voice unmuted `{member}`.")
    
    
    
    @voice.command(name="deafen", description="Deafen a member.", aliases=['deaf'], usage="voice deafen <@members/id>")
    @commands.has_guild_permissions(deafen_members=True)
    @app_commands.describe(members="Members you want to deafen.")
    async def deafen(self, ctx, members: commands.Greedy[discord.Member]):
        await ctx.defer()
        if not members:
            await ctx.send(f"{self.bot.warning} | Provide atleast one @member/id.")
            return
        for member in members:
            if not member.voice:
                await ctx.send(f"{self.bot.fail} | `{member}` not in voice channel.")
                continue
            if member.voice.deaf:
                await ctx.send(f"{self.bot.fail} | `{member}` is already voice deafened.")
                continue
            await member.edit(deafen=True, reason=f"{member}: Used voice deafen command.")
            await ctx.send(f"{self.bot.success} | Successfully voice deafened `{member}`.")
    
    
    @voice.command(name="undeafen", description="Undeafen a member.", aliases=['undeaf'], usage="voice undeafen <@members/ids>")
    @commands.has_guild_permissions(deafen_members=True)
    @app_commands.describe(members="Members you want to undeafen.")
    async def undeafen(self, ctx, members: commands.Greedy[discord.Member]):
        await ctx.defer()
        if not members:
            await ctx.send(f"{self.bot.warning} | Provide atleast one @member/id.")
            return
        for member in members:
            if not member.voice:
                await ctx.send(f"{self.bot.fail} | `{member}` not in voice channel.")
                continue
            if not member.voice.deaf:
                await ctx.send(f"{self.bot.fail} | `{member}` is not voice undeafened.")
                continue
            await member.edit(deafen=False, reason=f"{member}: Used voice undeaf command.")
            await ctx.send(f"{self.bot.success} | Successfully voice undeafened `{member}`.")
    
    
    @voice.command(name="move", description="Move all the members of users current vc to another selected vc.", usage="voice move <channel/id>")
    @commands.has_guild_permissions(move_members=True)
    @app_commands.describe(channel="Channel where you want to move.")
    async def move(self, ctx, channel: discord.VoiceChannel):
        if not ctx.author.voice:
            em = discord.Embed(title="Error!", description=f"You are not connected to any voice channel.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        if ctx.author.voice.channel == channel:
            em = discord.Embed(title="Failed", description=f"You are already in the same channel.", color = discord.Colour.red())
            await ctx.send(embed=em)
            return
        msg = await ctx.send(f"{self.bot.working} Moving all the connect users to `{channel}`, please be patient.")
        for member in ctx.author.voice.channel.members:
            await member.move_to(channel, reason=f"{ctx.author} used voice move command.")
        await msg.edit(content=f"{self.bot.success} | Successfully voice moved all connected users.")
    
    
async def setup(bot):
    await bot.add_cog(Voice(bot))