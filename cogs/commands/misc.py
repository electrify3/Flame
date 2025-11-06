import datetime
import typing

import discord

from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from utils import tools



class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime = datetime.datetime.utcnow()
        self.emoji = "<:Ediscover:1127305437549711372>"
        
    
    @commands.hybrid_command(name= "ping",description="Shows bot latency.", usage="ping", aliases=["uptime"])
    @commands.guild_only()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        uptime = str(datetime.datetime.utcnow() - self.uptime).split(".")[0]
        em = discord.Embed(title=f"{ctx.me}", color=discord.Colour.dark_theme())
        em.add_field(name="<:Eping:1138002794197041223> Ping", value=f"{latency}ms", inline=False)
        em.add_field(name="<a:Euptime:1138003049407848510> Uptime", value=f"{uptime}", inline=False)
        em.set_thumbnail(url=ctx.me.display_avatar.url)
        em.set_footer(text=f'Requested by: {ctx.author.name}')
        await ctx.send(embed=em)
    
    
    @commands.hybrid_group(name="avatar", description="Shows a user avatar.", aliases=["av", "pfp", "icon"], usage="avatar [user/id]")
    @commands.guild_only()
    @app_commands.describe(member="Select member whose pfp you want to see.")
    async def avatar(self, ctx,*, member: typing.Union[discord.Member, discord.User] = commands.Author):
        embed = discord.Embed(title = 'Avatar')
        embed.set_author(name = member, icon_url = member.display_avatar.url)
        embed.set_image(url = member.display_avatar.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @avatar.command(name="user", description="Shows a user avatar.", aliases=["member"], usage="avatar user [user/id]")
    @commands.guild_only()
    @app_commands.describe(member="Select member whose pfp you want to see.")
    async def av_user(self, ctx,*, member: typing.Union[discord.Member, discord.User] = commands.Author):
        embed = discord.Embed(title = 'Avatar')
        embed.set_author(name = member, icon_url = member.display_avatar.url)
        embed.set_image(url = member.display_avatar.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    
    @avatar.command(name="server", description="Displays server icon.", usage="avatar server", aliases=["guild", "sv"])
    @commands.guild_only()
    async def av_server(self, ctx):
        if not ctx.guild.icon:
            return await ctx.send(f"{self.bot.fail} | This server don't have a icon set!")
        embed = discord.Embed(title=ctx.guild)
        embed.set_image(url = ctx.guild.icon.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}')
        await ctx.send(embed=embed)
    
    
    @commands.hybrid_group(name="banner", description="Displays banner of a user.", aliases=["br"], usage="banner [member/id]")
    @commands.guild_only()
    @app_commands.describe(user="Select a user.")
    async def banner(self, ctx, user: discord.User=commands.Author):
        await ctx.defer()
        user = await self.bot.fetch_user(user.id)
        if not user.banner:
            return await ctx.send(f"{self.bot.warning} | No banner found!")
        embed = discord.Embed(title = 'Banner')
        embed.set_author(name = user, icon_url = user.display_avatar.url)
        embed.set_image(url = user.banner.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}',icon_url = ctx.author.display_avatar.url)
        await ctx.send(embed=embed)


    @banner.command(name="user", description="Displays banner of a user.", aliases=["member"], usage="banner [user/id]")
    @commands.guild_only()
    @app_commands.describe(user="Select a user.")
    async def banner_user(self, ctx, user: discord.User=commands.Author):
        await ctx.defer()
        user = await self.bot.fetch_user(user.id)
        if not user.banner:
            return await ctx.send(f"{self.bot.warning} | No banner found!")
        embed = discord.Embed(title = 'Banner')
        embed.set_author(name = user, icon_url = user.display_avatar.url)
        embed.set_image(url = user.banner.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}',icon_url = ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    
    @banner.command(name="server", description="Displays server banner.", usage="banner server", aliases=["guild", "sv"])
    @commands.guild_only()
    async def banner_server(self, ctx):
        if not ctx.guild.banner:
            return await ctx.send(f"{self.bot.fail} | This server don't have a banner set!")
        embed = discord.Embed(title=ctx.guild)
        embed.set_image(url = ctx.guild.banner.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}')
        await ctx.send(embed=embed)
    
    
    @commands.hybrid_command(name="background", description="Displays server invite background.", aliases=["invitebackground", "ib", "splash", "bg"], usage="background")
    @commands.guild_only()
    async def background(self, ctx):
        if not ctx.guild.splash:
            return await ctx.send(f"{self.bot.fail} | This server don't have a invite background set!")
        embed = discord.Embed(title=ctx.guild)
        embed.set_image(url = ctx.guild.splash.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}')
        await ctx.send(embed=embed)
    
    
    @commands.hybrid_command(name="discovery", description="Displays server discovery background.", aliases=["discoverybackground", "db", "discoverysplash", "dbg"], usage="discovery")
    @commands.guild_only()
    async def discovery(self, ctx):
        if not ctx.guild.discovery_splash:
            return await ctx.send(f"{self.bot.fail} | This server don't have a discovery background set!")
        embed = discord.Embed(title=ctx.guild)
        embed.set_image(url = ctx.guild.discovery_splash.url)
        embed.set_footer(text=f'Requested by: {ctx.author.name}')
        await ctx.send(embed=embed)
    
    
    @commands.hybrid_command(name="membercount", description="Shows the server member count.", aliases=["mc", "members", "memberscount"], usage="membercount")
    @commands.guild_only()
    async def membercount(self, ctx):
        total_members = ctx.guild.member_count
        online = len([member for member in ctx.guild.members if member.status == discord.Status.online])
        idle = len([member for member in ctx.guild.members if member.status == discord.Status.idle])
        dnd = len([member for member in ctx.guild.members if member.status == discord.Status.dnd])
        active_members = online + idle + dnd
        offline = total_members - active_members
        bots = len([member for member in ctx.guild.members if member.bot])
        icon = (ctx.guild.icon or ctx.me.display_avatar).url
        em = discord.Embed(title=ctx.guild, color=ctx.author.color, timestamp=datetime.datetime.utcnow())
        em.set_thumbnail(url=icon)
        em.add_field(name="Members Status", value=f"**Total members**: {ctx.guild.member_count}\n(<:Euser:1135804161661874256> {total_members-bots} | <:Ebot:1135802717932097608> {bots})", inline=False)
        em.add_field(name="Activity Status", value=f"**Online members**: {active_members}\n(<:Eonline:1137355060645466153> {online} | <:Eidle:1137355053666144286> {idle} | <:Ednd:1137355047752187944> {dnd} | <:Einvisible:1137354444917456906> {offline})", inline=False)
        em.set_footer(text=f"Server ID: {ctx.guild.id}")
        await ctx.send(embed=em)
    
    
    @commands.hybrid_command(name="boosters", description="Find all server boosters.", usage="boosters")
    @commands.guild_only()
    async def boosters(self, ctx):
        await ctx.defer()
        members = ctx.guild.premium_subscribers
        if not members:
            return await ctx.send(f"{self.bot.warning} | No current server boosters found!")
        message = ", "
        message = message.join(f"`{member}`" for member in members[:30])
        em = discord.Embed(title=ctx.guild, color=self.bot.color)
        em.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else ctx.me.display_avatar.url)
        em.add_field(name="Context", value=f"Server level: {ctx.guild.premium_tier}\nTotal boosts: {ctx.guild.premium_subscription_count}\nTotal boosters: {len(members)}\nBooster role: {ctx.guild.premium_subscriber_role.mention if ctx.guild.premium_subscriber_role else None}", inline=False)
        em.add_field(name="Boosters", value=message, inline=False)
        em.set_footer(text=f'Requested by: {ctx.author}')
        await ctx.send(embed=em)
    
    
    
    @commands.hybrid_command(name="firstmessage", description="Returns first message of a channel.", aliases=["fm"], usage="firstmessage [channel/id]")
    @app_commands.describe(channel="Select a channel.")
    @commands.guild_only()
    async def firstmessage(self, ctx, channel: discord.TextChannel=None):
        if channel is None: channel = ctx.channel
        
        async for message in channel.history(limit=1, oldest_first=True): pass
        
        em = discord.Embed(title=f"{channel.name}'s first message", description=message.content or "[No text found in the message]", color=self.bot.color)
        em.add_field(name="Author", value=message.author.name, inline=False)
        em.set_thumbnail(url=message.author.display_avatar.url)
        em.set_footer(text=f'Requested by: {ctx.author}')
        button = Button(label="View message", url=message.jump_url)
        view = View()
        view.add_item(button)
        await ctx.send(embed=em, view=view)
    
    
    @commands.hybrid_command(name="vanity", description="Shows the server's custom invite url.", aliases=["customurl"], usage="vanity")
    @commands.guild_only()
    async def vanity(self, ctx):
        url = ctx.guild.vanity_url
        if url: await ctx.send(url)
        else: await ctx.send(f"{self.bot.warning} | No vanity url found for this server.")
    
    
    
    async def member_info(self, ctx, member: discord.Member):
        top_hoist_role = None
        for role in reversed(member.roles):
            if role.hoist:
                top_hoist_role = role
                break
        permissions = member.guild_permissions
        acknowledgement = "Member"
        if member == ctx.guild.owner: acknowledgement = "Owner"
        elif permissions.administrator: acknowledgement = "Admin" 
        elif permissions.kick_members or permissions.ban_members: acknowledgement = "Moderator"
        elif permissions.manage_guild or permissions.manage_roles or permissions.manage_channels or permissions.manage_messages: acknowledgement = "Manager"
        em = discord.Embed(description=f"[Avatar]({member.display_avatar.url})", color = member.color, timestamp = datetime.datetime.utcnow())
        em.set_author(name=member, icon_url = member.display_avatar.url)
        em.set_thumbnail(url = member.display_avatar.url)
        em.add_field(name="Created at", value = f"<t:{int(member.created_at.timestamp())}> \n({(discord.utils.utcnow() - member.created_at).days} Days ago)", inline = False) 
        em.add_field(name="Joined at", value = f"<t:{int(member.joined_at.timestamp())}> \n({(discord.utils.utcnow() - member.joined_at).days} Days ago)", inline = False)
        em.add_field(name="Bot", value=f"{member.bot}", inline=False)
        em.add_field(name="Acknowledgements", value = f"Server {acknowledgement}", inline = False)
        em.add_field(name="Roles", value = f"Total roles: {len(member.roles) - 1}\nTop role: {member.top_role.mention if member.top_role else None}\nTop hoisted role: {top_hoist_role.mention if top_hoist_role else None}", inline = False)
        em.add_field(name="Permissions", value=', '.join(permission.replace("_", " ").capitalize() for permission, value in permissions if value) or "None", inline=False)
        em.set_footer(text=f"ID: {member.id}")
        member = await self.bot.fetch_user(member.id)
        if member.banner:
            em.set_image(url=member.banner.url)
        profile = Button(label="Profile", url=f"https://discordapp.com/users/{member.id}")
        view = View()
        view.add_item(profile)
        if member.bot:
            add_bot = Button(label=f"Add {member.name}", url=f"https://discord.com/api/oauth2/authorize?client_id={member.id}&permissions=1513962695871&scope=bot%20applications.commands")
            view.add_item(add_bot)
        await ctx.send(embed=em, view=view)
    
    
    async def user_info(self, ctx, id: int):
        member = await self.bot.fetch_user(id)
        em = discord.Embed(description=f"[Avatar]({member.display_avatar.url})", color = ctx.author.color, timestamp = datetime.datetime.now())
        em.set_author(name=member, icon_url = member.display_avatar.url)
        em.set_thumbnail(url = member.display_avatar.url)
        em.add_field(name="Created at", value = f"<t:{int(member.created_at.timestamp())}> \n({(discord.utils.utcnow() - member.created_at).days} Days ago)", inline = False)
        em.add_field(name="Bot", value=f"{member.bot}", inline=False)
        try:
            em.add_field(name="Banned", value=f"{await tools.is_banned(ctx, member)}", inline=False)
        except: pass
        em.set_footer(text=f"ID: {member.id}")
        if member.banner:
            em.set_image(url=member.banner.url)
        profile = Button(label="Profile", url=f"https://discordapp.com/users/{member.id}")
        view = View()
        view.add_item(profile)
        if member.bot:
            add_bot = Button(label=f"Add {member.name}", url=f"https://discord.com/api/oauth2/authorize?client_id={member.id}&permissions=1513962695871&scope=bot%20applications.commands")
            view.add_item(add_bot)
        await ctx.send(embed=em, view=view)
        
        
    @commands.hybrid_command(name="userinfo", description="Shows information about a user.", aliases=["ui", "whois"], usage="userinfo [user/id]")
    @commands.guild_only()
    @app_commands.describe(member="Select a member.")
    async def userinfo(self, ctx, member: discord.User=commands.Author):
        try:
            member = await commands.MemberConverter().convert(ctx, str(member.id))
            await self.member_info(ctx, member)
        except Exception as e:
            print(e)
            await self.user_info(ctx, member.id)
    
    
    @commands.hybrid_command(name="roleinfo", description="Shows information about a selected role.", aliases=["ri"], usage="roleinfo <role>")
    @commands.guild_only()
    @app_commands.describe(role = "Select a role.")
    async def roleinfo(self, ctx,*, role):
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
        
        text = ", ".join(f"`{member}`" for member in role.members[:30]) or "None"
        
        em = discord.Embed(color = role.color, timestamp = datetime.datetime.utcnow())
        em.set_thumbnail(url=role.display_icon.url if role.display_icon else ctx.guild.icon.url if ctx.guild.icon else ctx.me.display_avatar.url)
        em.add_field(name="Role ID", value=f"`{role.id}`", inline=False)
        em.add_field(name="Name", value=role, inline=False)
        if role.display_icon:
            em.add_field(name="Icon", value=f"[Icon url]({role.display_icon})", inline=False)
        em.add_field(name="Color", value=f"`{str(role.color)}`", inline=False)
        em.add_field(name="Role Mention", value=f"`{role.mention}`", inline=False)
        em.add_field(name="Hoisted", value=f"`{role.hoist}`", inline=False)
        em.add_field(name="Position", value=f"`{role.position}`", inline=False)
        em.add_field(name="Mentionable", value=f"`{role.mentionable}`", inline=False)
        em.add_field(name="Managed", value=f"`{role.managed}`", inline=False)
        em.add_field(name="Administrator", value=f"`{role.permissions.administrator}`", inline=False) 
        em.add_field(name="Created at", value=f"<t:{int(role.created_at.timestamp())}>\n({(discord.utils.utcnow() - role.created_at).days} Days ago)", inline=False)
        em.add_field(name=f"Members: {len(role.members)}", value=f"{text}", inline=False)
        em.add_field(name="Permissions", value=', '.join(permission.replace("_", " ").capitalize() for permission, value in role.permissions if value) or "None", inline=False)
        em.set_footer(text=f"Requested by: {ctx.author.name}")
        await ctx.send(embed=em)
    
    
    @commands.hybrid_command(name="serverinfo", description="Shows the server information.", aliases=["si"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        roles = [role for role in ctx.guild.roles if not role.is_bot_managed()]
        try: bans = len([entry async for entry in ctx.guild.bans(limit=None)])
        except: bans = "No perms for this info."
        channel_types = f"(<:Elist:1127305243978371245> {len(ctx.guild.categories)} | <:Etext:1135620680323453040> {len(ctx.guild.text_channels)} | <:Evoice:1127301699506274425> {len(ctx.guild.voice_channels)} | <:Estage:1135621034356256808> {len(ctx.guild.stage_channels)} | <:Eforum:1135621240711807047> {len(ctx.guild.forums)})"
        icon = ctx.guild.icon.url if ctx.guild.icon else ctx.me.display_avatar.url
        em = discord.Embed(description=ctx.guild.description, color=ctx.author.color)
        em.set_author(name=ctx.guild, icon_url=icon)
        em.set_thumbnail(url=icon)
        em.add_field(name="Server ID", value=ctx.guild.id, inline=False)
        em.add_field(name="Owner", value=f"{ctx.guild.owner} ({ctx.guild.owner.mention})", inline=False)
        em.add_field(name="Creation Date", value=f"<t:{int(ctx.guild.created_at.timestamp())}>\n({(discord.utils.utcnow() - ctx.guild.created_at).days} Days ago)", inline=False)
        em.add_field(name="Members", value=f"Total members: {ctx.guild.member_count}\nBots: {len([member for member in ctx.guild.members if member.bot])}\nBanned: {bans}", inline=False)
        em.add_field(name="Channels", value=f"Total channels: {len(ctx.guild.channels)}\n{channel_types}\nSystem messages channel: {ctx.guild.system_channel.mention if ctx.guild.system_channel else None}\nRules channel: {ctx.guild.rules_channel.mention if ctx.guild.rules_channel else None}\nInactivity channel: {ctx.guild.afk_channel.mention if ctx.guild.afk_channel else None}", inline=False)
        em.add_field(name="Emotes", value=f"Emojis ({len(ctx.guild.emojis)}/{ctx.guild.emoji_limit*2})\nStickers ({len(ctx.guild.stickers)}/{ctx.guild.sticker_limit})", inline=False)
        em.add_field(name="Server Boosts", value=f"Server level: {ctx.guild.premium_tier}\nTotal boosts: {ctx.guild.premium_subscription_count}\nBooster role: {ctx.guild.premium_subscriber_role.mention if ctx.guild.premium_subscriber_role else None}", inline=False)
        em.add_field(name="Roles", value=f"Total roles: {len(ctx.guild.roles)}\nAssignable roles: {len(roles)}\nBot roles: {len(ctx.guild.roles)-len(roles)}", inline=False)
        if ctx.guild.vanity_url: em.add_field(name="Vanity Url", value=ctx.guild.vanity_url, inline=False)
        em.add_field(name="Features", value=', '.join(feature.replace("_", " ").capitalize() for feature in ctx.guild.features) or "None", inline=False)
        em.set_footer(text=f"ID: {ctx.guild.id} | {ctx.guild}")
        if ctx.guild.banner: em.set_image(url=ctx.guild.banner.url)
        await ctx.send(embed=em)
    
    
async def setup(bot):
    await bot.add_cog(Misc(bot))