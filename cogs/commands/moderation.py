import datetime
import re
import typing

import discord

from discord import app_commands
from discord.ext import commands

from utils import tools


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Emoderation:1127302951371804793>"
    
    
    @commands.hybrid_command(name="mute", description="Mutes a member.", aliases=["timeout"], usage="timeout <members/ids> [time] [reason]")
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(members="Members you want to mute.", time="duration of mute eg. 1h30m", reason="Reason of mute.")
    async def mute(self, ctx, members: commands.Greedy[discord.Member], time="1h", *, reason="No reason specified."):
        members = set(members)
        
        if not members: return await ctx.send(f"{self.bot.warning} | Provide atleast one @user/id.")
        elif len(members) > 10 and ctx.author != ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can use this command on more than `10` users.")
        
        dtime = time
        time = tools.format_time(time)
        if time.total_seconds() == 0:
            reason = f"{dtime} {reason}"
            time = tools.format_time("1h")
        elif time.total_seconds() > 60*60*24*28: return await ctx.send(f"{self.bot.fail} | Timeout can't be more than 28days.")
        for member in members:
            if ctx.author.top_role.position <= member.top_role.position and ctx.author != ctx.guild.owner:
                await ctx.send(f"{self.bot.fail} | You can't mute `{member}`.")
                continue
            if member.is_timed_out():
                await ctx.send(f"{self.bot.warning} | `{member}` is already muted.")
                continue
            try:
                await member.timeout(time, reason=f"{ctx.author}: {reason}")
                await ctx.send(f"{self.bot.success} | Successfully muted `{member}` till <t:{int(time.total_seconds() + datetime.datetime.utcnow().timestamp())}>.")
            except:
                await ctx.send(f"{self.bot.fail} | Unable to mute `{member}`.")
    
    
    @commands.hybrid_command(name="unmute", description="Unmutes a member.", aliases=["untimeout"], usage="unmute <members/ids> [reason]")
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def unmute(self, ctx, members: commands.Greedy[discord.Member],*, reason="No reason specified."):
        members = set(members)
        
        if not members: return await ctx.send(f"{self.bot.warning} | Provide atleast one @user/id.")
        elif len(members) > 10 and ctx.author != ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can use this command on more than `10` users.")
        
        for member in members:
            if not member.is_timed_out():
                await ctx.send(f"{self.bot.fail} | `{member}` is not muted.")
                continue
            await member.timeout(None, reason=f"{ctx.author}: {reason}")
            await ctx.send(f"{self.bot.success} | Successfully unmuted `{member}`.")
    
    
    @commands.hybrid_command(name="kick", description="Kicks a member out.", usage="kick <members/ids> [reason]")
    @commands.has_permissions(kick_members = True)
    @commands.guild_only()
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason="No reason specified."):
        members = set(members)
        
        if not members: return await ctx.send(f"{self.bot.warning} | Provide atleast one @user/id.")
        elif len(members) > 10 and ctx.author != ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can use this command on more than `10` users.")
        
        for member in members:
            if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
                await ctx.send(f"{self.bot.fail} | You don't have permission to kick `{member}`.")
                continue
            if member.top_role >= ctx.guild.me.top_role or ctx.guild.owner is member:
                await ctx.send(f"{self.bot.fail} | I don't have permission to kick `{member}`.")
                continue
            
            try:
                await member.kick(reason=f"{ctx.author}: {reason}")
                await ctx.send(f"{self.bot.success} | Successfully kicked `{member}`.")
            except:
                await ctx.send(f"{self.bot.fail} | I am unable to kick `{member}`.")
    
    
    @commands.hybrid_command(name="ban", description="Bans a user.", aliases=["hackban"], usage="ban <users/ids> [days] [reason]")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(users="Users you want to ban.", days="Days of message deletion (max value 7).", reason="Reason of ban.")
    async def ban(self, ctx, users: commands.Greedy[discord.User], days: typing.Optional[int] = 1, *, reason="No reason specified."):
        users = set(users)
        
        if days > 7:
            days = 7
            await ctx.send(f"{self.bot.warning} | Message deletion days can't be more than `7` days, falling back to max allowed value `7`.")
        if not users: return await ctx.send(f"{self.bot.warning} | Provide atleast one @user/id.")
        elif len(users) > 10 and ctx.author != ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can't use this command on more than `10` users.")
        
        bans = [entry.user.id async for entry in ctx.guild.bans(limit=None)]
        for user in users:
            try:
                user = await commands.MemberConverter().convert(ctx, str(user.id))
                if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
                    await ctx.send(f"{self.bot.fail} | You don't have permission to ban `{user}`.")
                    continue
                if user.top_role >= ctx.guild.me.top_role or ctx.guild.owner is user:
                    await ctx.send(f"{self.bot.fail} | I don't have permission to ban `{user}`.")
                    continue
            except:
                pass
            
            if user.id in bans:
                await ctx.send(f"{self.bot.fail} | `{user}` is already banned.")
                continue
            
            try:
                await ctx.guild.ban(user, reason=f"{ctx.author}: {reason}", delete_message_days=days)
                await ctx.send(f"{self.bot.success} | Successfully banned `{user}`.")
            except:
                await ctx.send(f"{self.bot.fail} | I am unable to ban `{user}`.")
                
    
    @commands.hybrid_command(name="unban", description="Unbans a user.", usage="unban <users/ids> [reason]")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @app_commands.describe(users="users id(s)", reason="Reason of unban.")
    async def unban(self, ctx, users: commands.Greedy[discord.User], *, reason="No reason specified."):
        users = set(users)
        
        if not users: return await ctx.send(f"{self.bot.warning} | Provide atleast one @user/id.")
        elif len(users) > 10 and ctx.author != ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can use this command on more than `10` users.")
        
        bans = [entry.user.id async for entry in ctx.guild.bans(limit=None)]
        
        for user in users:
            if not user.id in bans:
                await ctx.send(f"{self.bot.fail} | `{user}` is not banned.")
                continue
            await ctx.guild.unban(user ,reason =f"{ctx.author}: {reason}")
            await ctx.send(f"{self.bot.success} | Successfully unbanned `{user}`.")
    
    
    @commands.hybrid_command(name="unbanall", description="Unbans all banned users.", aliases=["uball"], usage="unbanall")
    async def unbanall(self, ctx):
        if ctx.guild.owner != ctx.author:
            await ctx.send(f"{self.bot.fail} | Only server owner can use this command!")
            return
        banned_users = [ban.user async for ban in ctx.guild.bans(limit=None)]
        message = await ctx.send(f"{self.bot.working} | Removing bans from **{len(banned_users)}** Users, please be patient.")
        for user in banned_users:
            await ctx.guild.unban(user ,reason =f"{ctx.author} used unbanall command.")
        await message.edit(content=f"{self.bot.success} | Successfully unbanned **{len(banned_users)}** users.")
    
    
    @commands.hybrid_command(name="warn", description="Warns a user.", usage="warn <member/id> [reason]")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @app_commands.describe(member="Member you want to warn.", reason="Reason of warning.")
    async def warn(self, ctx, member : discord.Member,*, reason="[No reason specified]"):
        if member.bot: return await ctx.send(f"{self.bot.fail} | You can't warn a bot!")
        elif member == ctx.author: return await ctx.send(f"{self.bot.fail} | You can't warn yourself!")
        elif ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can't warn `{member}`.")
        elif member == ctx.guild.owner: return await ctx.send(f"{self.bot.fail} | You can't warn owner.")
        
        embed = discord.Embed(color = discord.Colour.red())
        embed.set_author(name=f'{member} has been warned!',icon_url = member.display_avatar.url)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        try :
            em = discord.Embed(title="Warning!", description=f"You have been warned in {ctx.guild.name}.", color=discord.Colour.red())
            em.add_field(name="Reason", value=f"{reason}", inline=False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline=False)
            await member.send(embed=em)
        except: pass
        await ctx.send(member.mention, embed=embed)
    
    
    
    @commands.hybrid_group(name="purge", description="Delete messages of a channel in a selected range.", aliases =["clear"], usage="purge <limit>", with_app_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        
        def check(message):
            return not message.pinned
        
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    
    @purge.command(name="any", description="Delete messages of a channel.", usage="purge any [limit]")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def any(self, ctx, limit: int):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    
    @purge.command(name="user", description="Delete messages of a channel sent by specific users.", usage="purge user <users> [limit]", aliases=["users"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def user(self, ctx, users: commands.Greedy[discord.User], limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        users = set(users)
        if not users: return await ctx.send(f"{self.bot.fail} | Invalid command usage, `users` are not specified!")
        
        def check(message):
            return not message.pinned and message.author in users
        
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    
    @purge.command(name="content", description="Delete messages of a channel containing specified content.", usage="purge content <text> [limit]", aliases=["text", "include", "contains"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def content(self, ctx, *, text: str, limit: int = 100):
        try:
            limit = int(text.split(" ")[-1].strip(" "))
            text = text.replace(text.split(" ")[-1], "")
        except: pass
        
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        if not text: return await ctx.send(f"{self.bot.fail} | Invalid command usage, `content` is not specified!")
        
        def check(message):
            if text: return not message.pinned and text.lower() in message.content.lower()
            else: return not message.pinned
        
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    
    @purge.command(name="attachment", aliases = ["media", "attachments", "file"], description="Delete messages of a channel containing attachment.", usage="purge attachment [limit]")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def attachment(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned and message.attachments
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="link", aliases = ["urls", "url", "links"], description="Delete messages of a channel containing links.", usage="purge link [limit]")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def link(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return any(url in message.content.lower().replace(" ", "") for url in ["https://", "http://"]) and not message.pinned
        
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="invite", description="Delete messages of a channel containing discord invites.", usage="purge invite [limit]", aliases=["invites"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def invite(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned and any(url in message.content.lower().replace(" ", "") for url in ["discord.gg/", "discord.com/invite/"])
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="bot", aliases = ["nonhuman", "bots"], description="Delete messages of a channel sent by bots.", usage="purge bot [limit]")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def bot(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned and message.author.bot
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="human", description="Delete messages of a channel sent by humans.", usage="purge human [limit]", aliases=["humans"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def human(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned and not message.author.bot
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="embed", aliases = ["em"], description="Delete messages of a channel containing embeds.", usage="purge embed [limit]")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned and message.embeds
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="sticker", description="Delete messages of a channel containing stickers.", usage="purge sticker [limit]", aliases=["sickers"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def sticker(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            return not message.pinned and message.stickers
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    
    
    @purge.command(name="emoji", aliases = ["emote", "emojis"], description="Delete messages of a channel containing emojis.", usage="purge emoji [limit]")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def emoji(self, ctx, limit: int = 100):
        if limit > 1000: return await ctx.send(f"{self.bot.fail} | You can't delete more than **1000** messages at once.")
        def check(message):
            content = message.content.lower()
            emote = re.compile(r'<a?:\w+:\d+>')
            normal = re.compile(r'[\U0001F300-\U0001F6FF]')
            return not message.pinned and (re.search(emote, content) or re.search(normal, content))
        
        await ctx.defer()
        if ctx.interaction:
            await ctx.interaction.delete_original_response()
        else:
            await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, after = datetime.datetime.now()-datetime.timedelta(days=14), oldest_first=False, check=check)
        if len(purged) == 0: await ctx.send(f"{self.bot.fail} | No message found!")
        else: await ctx.send(f"{self.bot.success} | Successfully deleted **{len(purged)}** messages.", delete_after=5)
    

async def setup(bot):
    await bot.add_cog(Moderation(bot))