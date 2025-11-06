import io
import datetime

import aiosqlite
import chat_exporter
import discord

from discord.ext import commands


class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}
        self.path = "data/database/Logging.db"
    
    
    async def fetch_data(self, category, guild):
        async with aiosqlite.connect(self.path) as db:
            if category == "Join":
                async with db.execute(f"""SELECT `Join` FROM Logging WHERE Guild = {guild.id}""") as c:
                    data = await c.fetchone()
            else:
                async with db.execute(f"""SELECT {category} FROM Logging WHERE Guild = {guild.id}""") as c:
                    data = await c.fetchone()
        return data
    
    
    async def send_log(self, category, guild, embed):
        data = await self.fetch_data(category, guild)
        if data:
            logchannel = self.bot.get_channel(data[0])
            if logchannel:
                await logchannel.send(embed=embed)
    
    
    @commands.Cog.listener("on_ready")
    async def setup_bot(self):
        for guild in self.bot.guilds:
            if not guild.me.guild_permissions.manage_guild:
                continue
            self.invites[str(guild.id)] = {}
            for invite in await guild.invites():
                self.invites[str(guild.id)][invite.id] = invite.uses
                
    @commands.Cog.listener("on_invite_create")
    async def update_data(self, invite):
        self.invites[str(invite.guild.id)][invite.id] = invite.uses
    
    @commands.Cog.listener("on_guild_join")
    async def update_guild_data(self, guild):
        if not guild.me.guild_permissions.manage_guild:
            return
        self.invites[str(guild.id)] = {}
        for invite in await guild.invites():
            self.invites[str(guild.id)][invite.id] = invite.uses
    
    
    # Server Logs ->
    
    @commands.Cog.listener("on_guild_channel_create")
    async def channel_creaton(self, channel):
        if not channel.guild.me.guild_permissions.view_audit_log: return
        creator = None
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            if entry.target.id == channel.id:
                creator = entry.user
        icon = (channel.guild.icon or self.bot.user.display_avatar).url
        
        embed = discord.Embed(title="A channel was created!", color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Name", value=channel.name, inline=False)
        embed.add_field(name="Category", value=channel.category, inline=False)
        embed.add_field(name="Position", value=channel.position, inline=False)
        embed.add_field(name="Creator", value=f"{creator} [{creator.id if creator else 0}]", inline=False)
        embed.set_thumbnail(url=icon)
        embed.set_footer(text=f"ID: {channel.id}")
        await self.send_log("Server", channel.guild, embed)
    
    
    @commands.Cog.listener("on_guild_channel_delete")
    async def channel_deletion(self, channel):
        if not channel.guild.me.guild_permissions.view_audit_log: return
        moderator = None
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
            if entry.target.id == channel.id:
                moderator = entry.user
        icon = (channel.guild.icon or self.bot.user.display_avatar).url
        
        embed = discord.Embed(title="A channel was deleted!", color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Name", value=channel.name, inline=False)
        embed.add_field(name="Category", value=channel.category, inline=False)
        embed.add_field(name="Position", value=channel.position, inline=False)
        embed.add_field(name="Moderator", value=f"{moderator} [{moderator.id if moderator else 0}]", inline=False)
        embed.set_thumbnail(url=icon)
        embed.set_footer(text=f"ID: {channel.id}")
        await self.send_log("Server", channel.guild, embed)
    
    
    @commands.Cog.listener("on_guild_channel_update")
    async def channel_update(self, before, after):
        if not after.guild.me.guild_permissions.view_audit_log:
            return
        
        moderator = None
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
            if entry.target.id == after.id:
                moderator = entry.user
        
        if not moderator:
            return
            
        icon = (after.guild.icon or self.bot.user.display_avatar).url
        
        if before.name != after.name:
            em = discord.Embed(title="A channel was renamed!", description=f"{before.mention} was renamed by {moderator.mention}", color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"`{before.name}` -> `{after.name}`", inline=False)
            em.set_thumbnail(url=icon)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
        
        if before.position != after.position:
            em = discord.Embed(title="A channel position was updated!", description=f"{before.mention} position was updated by {moderator.mention}", color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"`{before.position}` -> `{after.position}`", inline=False)
            em.set_thumbnail(url=icon)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
        
        if before.overwrites != after.overwrites:
            em = discord.Embed(title="Channel permissions updated!", description=f"{after.mention} was updated by {moderator.mention}", color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.set_thumbnail(url=icon)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
    
    
    @commands.Cog.listener("on_guild_role_create")
    async def role_create(self, role):
        if not role.guild.me.guild_permissions.view_audit_log: return
        moderator = None
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
            if entry.target.id == role.id:
                moderator = entry.user
        icon = (role.guild.icon or self.bot.user.display_avatar).url
        embed = discord.Embed(title="A role was created!", description=f"{role.mention} was created by {moderator}", color=role.color, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Name", value=role.name, inline=False)
        embed.add_field(name="Position", value=role.position, inline=False)
        embed.add_field(name="Hex", value=role.color, inline=False)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
        embed.add_field(name="Hoisted", value=role.hoist, inline=False)
        embed.add_field(name="Permissions", value=', '.join(permission.replace("_", " ").title() for permission, value in role.permissions if value) or "None", inline=False)
        embed.set_thumbnail(url=icon)
        embed.set_footer(text=f"ID: {role.id}")
        await self.send_log("Server", role.guild, embed)
    
    
    @commands.Cog.listener("on_guild_role_delete")
    async def role_delete(self, role):
        if not role.guild.me.guild_permissions.view_audit_log: return
        moderator = None
        async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
            if entry.target.id == role.id:
                moderator = entry.user
        icon = (role.guild.icon or self.bot.user.display_avatar).url
        embed = discord.Embed(title="A role was deleted!", description=f"{role} was deleted by {moderator}", color=role.color, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Name", value=role.name, inline=False)
        embed.add_field(name="Position", value=role.position, inline=False)
        embed.add_field(name="Hex", value=role.color, inline=False)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
        embed.add_field(name="Hoisted", value=role.hoist, inline=False)
        embed.add_field(name="Members", value=len(role.members), inline=False)
        embed.add_field(name="Permissions", value=', '.join(permission.replace("_", " ").title() for permission, value in role.permissions if value) or "None", inline=False)
        embed.set_thumbnail(url=icon)
        embed.set_footer(text=f"ID: {role.id}")
        await self.send_log("Server", role.guild, embed)
    
    
    @commands.Cog.listener("on_guild_role_update")
    async def role_update(self, before, after):
        if not after.guild.me.guild_permissions.view_audit_log:
            return
        
        moderator = None
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
            if entry.target.id == after.id:
                moderator = entry.user
        if not moderator:
            return
            
        if before.icon != after.icon:
            icon = after.icon
            if not icon:
                em = discord.Embed(title="Role icon updated!", description=f"{after.mention} icon was removed by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
                em.set_footer(text=f"ID: {after.id}")
            else:
                em = discord.Embed(title="Role icon updated!", description=f"{after.mention} icon was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
                em.set_thumbnail(url=icon.url)
                em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
            
        if before.name != after.name:
            em = discord.Embed(title="Role name updated!", description=f"{after.mention} name was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"`{before}` -> `{after}`", inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
        
        if before.color != after.color:
            em = discord.Embed(title="Role hex updated!", description=f"{after.mention} was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"`{before.color}` -> `{after.color}`", inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
        
        if before.position != after.position:
            em = discord.Embed(title="Role position updated!", description=f"{after.mention} was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"`{before.position}` -> `{after.position}`", inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
        
        if before.mentionable != after.mentionable:
            em = discord.Embed(title="Role updated!", description=f"{after.mention} was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"Anyone can mention: {after.mentionable}", inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
        
        if before.hoist != after.hoist:
            em = discord.Embed(title="Role updated!", description=f"{after.mention} was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Change", value=f"Display seperately: {after.hoist}", inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Server", after.guild, em)
            
        if before.permissions != after.permissions:
            added = set(perms for perms, value in after.permissions if value) - set(perms for perms, value in before.permissions if value)
            
            removed = set(perms for perms, value in before.permissions if value) - set(perms for perms, value in after.permissions if value)
            
            if added:
                em = discord.Embed(title="Role permissions updated!", description=f"{after.mention} was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
                em.add_field(name="Added permissions", value=", ".join(permission.replace('_', ' ').title() for permission in added), inline=False)
                em.set_footer(text=f"ID: {after.id}")
                await self.send_log("Server", after.guild, em)
            
            if removed:
                em = discord.Embed(title="Role permissions updated!", description=f"{after.mention} was updated by {moderator.mention}", color=after.color, timestamp=datetime.datetime.utcnow())
                em.add_field(name="Removed permissions", value=", ".join(permission.replace('_', ' ').title() for permission in removed), inline=False)
                em.set_footer(text=f"ID: {after.id}")
                await self.send_log("Server", after.guild, em)
        
    
    # Moderation Logs ->
    
    
    @commands.Cog.listener("on_member_update")
    async def member_timedout(self, before, after):
        if not after.guild.me.guild_permissions.view_audit_log: return
        icon = after.display_avatar.url
        moderator = None
        reason = "No reason specified."
        
        if not before.timed_out_until and after.timed_out_until:
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                if entry.target.id == after.id:
                    moderator = entry.user
                    reason = entry.reason
            em = discord.Embed(title="A member was muted!", color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.add_field(name="Offender", value=f"{after}", inline=False)
            em.add_field(name="Muted till", value=f"<t:{int(after.timed_out_until.timestamp())}>", inline=False)
            em.add_field(name="Moderator", value=f"{moderator}", inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.set_thumbnail(url=icon)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Moderation", after.guild, em)
        elif before.timed_out_until and not after.timed_out_until:
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                if entry.target.id == after.id:
                    moderator = entry.user
                    reason = entry.reason
            em = discord.Embed(title="A member was unmuted!", color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
            em.add_field(name="Member", value=f"{after}", inline=False)
            em.add_field(name="Moderator", value=f"{moderator}", inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.set_thumbnail(url=icon)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Moderation", after.guild, em)
    
    # Leave Log ->
    
    @commands.Cog.listener("on_member_remove")
    async def member_kicked_or_left(self, member):
        
        em = discord.Embed(description=f"{member.mention} {member}",color=self.bot.color, timestamp=datetime.datetime.utcnow())
        em.set_author(name="Member left", icon_url=member.display_avatar.url)
        em.set_thumbnail(url=member.display_avatar.url)
        em.set_footer(text=f"ID: {member.id}")
        await self.send_log("Leave", member.guild, em)
        
        
        if not member.guild.me.guild_permissions.view_audit_log: return
        moderator = None
        reason = "No reason specified."
        async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
            if entry.target != member: return
            moderator = entry.user
            reason = entry.reason
        
        if moderator:
            em = discord.Embed(title="A member was kicked!", color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
            em.add_field(name="Offender", value=f"{member} ({member.mention})", inline=False)
            em.add_field(name="Moderator", value=f"{moderator} ({moderator.mention})", inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.set_thumbnail(url=member.display_avatar.url)
            em.set_footer(text=f"ID: {member.id}")
            await self.send_log("Moderation", member.guild, em)
    
    
    @commands.Cog.listener("on_member_ban")
    async def member_banned(self, guild, user):
        if not guild.me.guild_permissions.view_audit_log: return
        moderator = None
        reason = "No reason specified."
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
            moderator = entry.user
            reason = entry.reason
        
        if moderator:
            em = discord.Embed(title="A member was banned!", color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
            em.add_field(name="Offender", value=f"{user} ({user.mention})", inline=False)
            em.add_field(name="Moderator", value=f"{moderator} ({moderator.mention})", inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.set_thumbnail(url=user.display_avatar.url)
            em.set_footer(text=f"ID: {user.id}")
            await self.send_log("Moderation", guild, em)
            
            # Ban log ->
            
            em = discord.Embed(title="Member Banned", description=f"{user.mention} {user}", color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
            em.set_thumbnail(url=user.display_avatar.url)
            em.set_footer(text=f"ID: {user.id}")
            await self.send_log("Ban", guild, em)
    
    
    @commands.Cog.listener("on_member_unban")
    async def member_unbanned(self, guild, user):
        if not guild.me.guild_permissions.view_audit_log: return
        moderator = None
        reason = "No reason specified."
        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=1):
            moderator = entry.user
            reason = entry.reason
        
        if moderator:
            em = discord.Embed(title="A member was unbanned!", color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
            em.add_field(name="User", value=f"{user} ({user.mention})", inline=False)
            em.add_field(name="Moderator", value=f"{moderator} ({moderator.mention})", inline=False)
            em.add_field(name="Reason", value=reason, inline=False)
            em.set_thumbnail(url=user.display_avatar.url)
            em.set_footer(text=f"ID: {user.id}")
            await self.send_log("Moderation", guild, em)
            
    # Members log ->
    
    @commands.Cog.listener("on_member_update")
    async def members_log(self, before, after):
        if before.display_avatar.url != after.display_avatar.url:
            em = discord.Embed(title="Member updated!", description=f"{after.mention} update their avatar\n[before]({before.display_avatar.url}) -> [after]({after.display_avatar.url})",color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.set_thumbnail(url=after.display_avatar.url)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Member", after.guild, em)
        
        elif before.nick != after.nick:
            em = discord.Embed(title="Member updated!", description=f"{after.mention} update their nickname\n`{before.nick}` -> `{after.nick}`",color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.set_thumbnail(url=after.display_avatar.url)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Member", after.guild, em)
            
        added = set(after.roles) - set(before.roles)
        removed = set(before.roles) - set(after.roles)
        if added:
            role_names = ', '.join(f"{role.mention}" for role in added)
            em = discord.Embed(description=f"Roles were added to {after.mention}", color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
            em.set_author(name=after, icon_url=after.display_avatar.url)
            em.add_field(name="Roles", value=role_names, inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Role", after.guild, em)
        
        if removed:
            role_names = ', '.join(f"{role.mention}" for role in removed)
            em = discord.Embed(description=f"Roles were removed from {after.mention}", color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
            em.set_author(name=after, icon_url=after.display_avatar.url)
            em.add_field(name="Roles", value=role_names, inline=False)
            em.set_footer(text=f"ID: {after.id}")
            await self.send_log("Role", after.guild, em)
            
    
    # Message log ->
    
    
    @commands.Cog.listener("on_message_delete")
    async def message_log(self, message):
        if message.author.bot: return
        em = discord.Embed(title="Message deleted!", description=f"Message sent by {message.author.mention} was deleted in {message.channel.mention}",color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
        em.set_author(name=message.author, icon_url=message.author.display_avatar.url)
        em.add_field(name="Content", value=message.content[:1024] or "**[No text found in deleted message]**", inline=False)
        em.set_footer(text=f"ID: {message.author.id} | Message ID: {message.id}")
        await self.send_log("Message", message.guild, em)
        
        em = discord.Embed(title="Message deleted!", description=f"Message sent by {message.author.mention} was deleted in {message.channel.mention}",color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
        em.set_author(name=message.author, icon_url=message.author.display_avatar.url)
        em.set_footer(text=f"ID: {message.author.id} | Message ID: {message.id}")
        
        if message.attachments:
            for attachment in message.attachments:
                em.set_image(url=attachment.url)
                await self.send_log("Message", message.guild, em)
        elif message.stickers:
            for sticker in message.stickers:
                em.set_image(url=sticker.url)
            await self.send_log("Message", message.guild, em)
    
    
    @commands.Cog.listener("on_message_edit")
    async def message_edit_log(self, before, after):
        if before.content == after.content or after.author.bot: return
        em = discord.Embed(title="Message edited!", description=f"Message sent by {after.author.mention} was edited in {after.channel.mention}",color=self.bot.color, timestamp=datetime.datetime.utcnow())
        em.set_author(name=after.author, icon_url=after.author.display_avatar.url)
        em.add_field(name="Before", value=before.content[:1024] or "**[No text found in original message]**", inline=False)
        em.add_field(name="After", value=after.content[:1024] or "**[No text found in edited message]**", inline=False)
        em.set_footer(text=f"ID: {after.id}")
        await self.send_log("Message", after.guild, em)
    
    
    @commands.Cog.listener("on_bulk_message_delete")
    async def purge_log(self, messages):
        message = messages[0]
        em = discord.Embed(title="Channel purged!", description=f"{len(messages)} Messages were purged in {message.channel.mention}",color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
        await self.send_log("Message", message.guild, em)
        
        transcript = await chat_exporter.raw_export(
            message.channel,
            messages = messages[::-1],
            bot = self.bot
        )
    
        if transcript:
            file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"purged-{message.channel.name}.html",
            )
        data = await self.fetch_data("Message", message.guild)
        if data:
            logchannel = self.bot.get_channel(data[0])
            if logchannel:
                await logchannel.send(file=file)
    
    
    # Invite and Join log ->
    
    
    @commands.Cog.listener("on_member_join")
    async def invite_log(self, member):
        em = discord.Embed(description=f"{member.mention} {member}",color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
        em.set_author(name="Member joined", icon_url=member.display_avatar.url)
        em.add_field(name="Created on", value=f"<t:{int(member.created_at.timestamp())}>", inline=False)
        em.set_thumbnail(url=member.display_avatar.url)
        em.set_footer(text=f"ID: {member.id}")
        await self.send_log("Join", member.guild, em)
        
        if not member.guild.me.guild_permissions.manage_guild:
            return
        else:
            for invite in await member.guild.invites():
                data = self.invites[str(member.guild.id)].get(invite.id)
                if data:
                    if invite.uses > data:
                        em = discord.Embed(title="Member joined", description=f"{member} ({member.mention})",color=self.bot.color, timestamp=datetime.datetime.utcnow())
                        em.add_field(name="Inviter", value=f"{invite.inviter} ({invite.inviter.mention})", inline=False)
                        em.add_field(name="Created on", value=f"<t:{int(member.created_at.timestamp())}>", inline=False)
                        em.add_field(name="Link used", value=invite.url, inline=False)
                        em.set_thumbnail(url=member.display_avatar.url)
                        em.set_footer(text=f"ID: {member.id}")
                        self.invites[str(member.guild.id)][invite.id] = invite.uses
                        await self.send_log("Invite", member.guild, em)
                    
    
    # Voice log
    
    @commands.Cog.listener("on_voice_state_update")
    async def voice_log(self, member, before, after):
        if before.channel == after.channel:
            return
        
        if before.channel and not after.channel:
            em = discord.Embed(description=f"{member.mention} left voice channel {before.channel.mention}", color=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
            em.set_author(name=member, icon_url=member.display_avatar.url)
            em.set_footer(text=f"ID: {member.id}")
        
        elif before.channel and after.channel:
            em = discord.Embed(description=f"{member.mention} switched voice channel {before.channel.mention} -> {after.channel.mention}", color=self.bot.color, timestamp=datetime.datetime.utcnow())
            em.set_author(name=member, icon_url=member.display_avatar.url)
            em.set_footer(text=f"ID: {member.id}")
        
        else:
            em = discord.Embed(description=f"{member.mention} joined voice channel {after.channel.mention}", color=discord.Colour.green(), timestamp=datetime.datetime.utcnow())
            em.set_author(name=member, icon_url=member.display_avatar.url)
            em.set_footer(text=f"ID: {member.id}")
        
        await self.send_log("Voice", member.guild, em)
    
    
async def setup(bot):
    await bot.add_cog(Logger(bot))