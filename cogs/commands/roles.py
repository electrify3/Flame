import io
import typing

import discord

from discord import app_commands
from discord.ext import commands
from PIL import Image

from utils import tools

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Erole:1127303371892736113>"
    
    @commands.hybrid_group(name="role", description="Adds or removes a role from a user.", usage="role <members/ids> <role>")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @commands.guild_only()
    async def role(self, ctx, members: commands.Greedy[discord.Member], *, role):
        name = role
        role = tools.find_role(ctx, role)
        members = [*set(members)]
        if not members:
            await ctx.send(f"{self.bot.warning}| Provide atleast one @user/id.")
            return
        if not role:
            await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            return
        if not await tools.is_addable(ctx, role):
            return
        
        for member in members:
            if role in member.roles :
                await member.remove_roles(role, reason=f"{ctx.author} used role.")
                await ctx.send(f'{self.bot.success} | Successfully removed {role} from `{member}`.')
            else:
                await member.add_roles(role, reason=f"{ctx.author} used role.")
                await ctx.send(f'{self.bot.success} | Successfully added {role} to `{member}`.')
    
    
    @role.command(name="add", description="Adds a role to the member.", usage="role add <member/id> <role>")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="Select a member.", role="Role you want to add.")
    async def add(self, ctx, member: discord.Member, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
        if not await tools.is_addable(ctx, role):
            return
        await member.add_roles(role, reason=f"{ctx.author} used role command.")
        await ctx.send(f'{self.bot.success} | Successfully added {role} to `{member}`.')
    
    
    @role.command(name="remove", description="Removes a role to the member.", usage="role remove <member/id> <role>")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(member="Select a member.", role="Role you want to remove.")
    async def remove(self, ctx, member: discord.Member, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
        if not await tools.is_addable(ctx, role):
            return
        await member.remove_roles(role, reason=f"{ctx.author} used role command.")
        await ctx.send(f'{self.bot.success} | Successfully removed {role} from `{member}`.')
    
    
    @role.command(name="position", description="Updates role position.", usage="role position <role> <new position>")
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(role="Name of the role.", position="New position of the role.")
    async def position(self, ctx, role: str, position:int):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
        if not await tools.is_editable(ctx, role) or not await tools.has_position(ctx, role):
            return
        await role.edit(position=position, reason=f"{ctx.author} used roleposition.")
        await ctx.send(f'{self.bot.success} | Successfully changed `{role}` position to **{position}**.')
    
    
    @role.command(name="reset", description="Resets a role permissions.", usage="role reset <role>")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Name of the role.")
    async def reset(self, ctx, *, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
        if not await tools.is_editable(ctx, role) or not await tools.has_position(ctx, role):
            return
        permissions = discord.Permissions(permissions=0)
        await role.edit(permissions=permissions, reason=f"{ctx.author} used rolereset.")
        await ctx.send(f'{self.bot.success} | Successfully reset `{role}` permissions.')
    
    
    @role.command(name="rename", description="Renames a role.", usage="role rename <role> <new name>", aliases=["name"])
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(role="Name of the role.", name="New name for the role.")
    async def rename(self, ctx, role: str, *, name):
        await ctx.defer()
        rname = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {rname} not found!")
        if not await tools.is_editable(ctx, role) or not await tools.has_position(ctx, role):
            return
        initial_name = role.name
        await role.edit(name=name, reason=f"{ctx.author} used rolename.")
        await ctx.send(f'{self.bot.success} | Successfully changed `{initial_name}` name to `{name}`.')
    
    
    @role.command(name="icon", description="Updates a role icon, leave emoji blank to remove role icon.", usage="role icon <role> [emoji]")
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(role="Name of the role.", emoji="Emoji you want to use as role icon, leave it blank to remove role icon.")
    async def icon(self, ctx, role: str, emoji: discord.PartialEmoji=None):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            return await ctx.send(f"{self.bot.fail} | Role {name} not found!")
        if not await tools.is_editable(ctx, role) or not await tools.has_position(ctx, role):
            return
        usable = emoji
        if emoji:
            if emoji.animated:
                data = await emoji.read()
                gif_image = Image.open(io.BytesIO(data))
                gif_image.seek(0)
                png_image = gif_image.convert("RGBA")
                png_bytes = io.BytesIO()
                png_image.save(png_bytes, format="PNG")
                emoji = png_bytes.getvalue()
            else:
                emoji = await emoji.read()
        await role.edit(display_icon=emoji, reason=f"{ctx.author} used roleicon.")
        await ctx.send(f"{self.bot.success} | Successfully changed `{role}` icon to {usable}.")
    
    
    @role.command(name="everyone", description="Add or remove a role from everyone.", aliases=["all"], usage="role everyone <add/remove> <role>")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @app_commands.describe(action="Select an action.", role="Name of the role.")
    async def everyone(self, ctx, action: typing.Literal["add", "remove"], *, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            return
        if not await tools.is_addable(ctx, role):
            return
        if action == "add":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Adding {role.mention} to all members, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in ctx.guild.members:
                if role in member.roles:
                    continue
                try:
                    await member.add_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully added a role for everyone.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
            
        elif action == "remove":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Removing {role.mention} from all members, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in role.members:
                try:
                    await member.remove_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully removed a role from everyone.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
        await message.edit(embed=em)
    
    
    @role.command(name="bot", description="Add or removes a role from bots.", aliases=["bots"], usage="role bot <add/remove> <role>")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @app_commands.describe(action="Select an action.", role="Name of the role.")
    async def bot(self, ctx, action: typing.Literal["add", "remove"], *, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            return
        if not await tools.is_addable(ctx, role):
            return
        if action == "add":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Adding {role.mention} to all bots, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in ctx.guild.members:
                if role in member.roles:
                    continue
                if not member.bot:
                    continue
                try:
                    await member.add_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully added a role for bots.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
            
        elif action == "remove":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Removing {role.mention} from all bots, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in role.members:
                if not member.bot:
                    continue
                try:
                    await member.remove_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully removed a role from bots.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
        await message.edit(embed=em)
    
    
    @role.command(name="human", description="Add or removes a role from humans.", aliases=["humans"], usage="role human <add/remove> <role>")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @app_commands.describe(action="Select an action.", role="Name of the role.")
    async def human(self, ctx, action: typing.Literal["add", "remove"], *, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            return
        if not await tools.is_addable(ctx, role):
            return
        if action == "add":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Adding {role.mention} to all humans, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in ctx.guild.members:
                if role in member.roles:
                    continue
                if member.bot:
                    continue
                try:
                    await member.add_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully added a role for humans.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
            
        elif action == "remove":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Removing {role.mention} from all humans, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in role.members:
                if member.bot:
                    continue
                try:
                    await member.remove_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully removed a role from humans.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
        await message.edit(embed=em)
    
    
    @role.command(name="target", description="Add or removes a role from a targeted role.", usage="role target <add/remove> <targeted role> <role>")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @app_commands.describe(action="Select an action.", target="Select an target role.", role="Name of the role.")
    async def target(self, ctx, action: typing.Literal["add", "remove"], target: str, *, role: str):
        await ctx.defer()
        name = role
        role = tools.find_role(ctx, role)
        if not role:
            await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            return
        name = target
        target = tools.find_role(ctx, target)
        if not target:
            await ctx.send(f"{self.bot.fail} | Role {name} not found!")
            return
        
        if not await tools.is_addable(ctx, role):
            return
        if action == "add":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Adding {role.mention} to all {target.mention} holders, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in target.members:
                if role in member.roles:
                    continue
                try:
                    await member.add_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully added a role for {target.mention} holders.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
            
        elif action == "remove":
            em = discord.Embed(title="Processing", description=f"{self.bot.working} | Removing {role.mention} from all {target.mention} holders, it may take a while.", color=self.bot.color)
            message = await ctx.send(embed=em)
            success = 0
            for member in target.members:
                if role not in member.roles:
                    continue
                try:
                    await member.remove_roles(role, reason=f"{ctx.author} used role command.")
                    success += 1
                except:
                    continue
            em = discord.Embed(title="Success",description=f"I successfully removed a role from {target.mention} holders.", color=self.bot.color)
            em.add_field(name="Role", value=role.mention, inline = False)
            em.add_field(name="Successful case", value=success, inline = False)
            em.add_field(name="Moderator", value=ctx.author.mention, inline = False)
        await message.edit(embed=em)
        
    
async def setup(bot):
    await bot.add_cog(Role(bot))