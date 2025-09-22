import discord
from utils import tools
from discord.ext import commands
from discord.ui import View, Button, Select
from discord import app_commands



class Menu(Select):
    def __init__(self, options, ctx, cogs):
        super().__init__(
        options = options,
        placeholder = "Select a category for more info"
        )
        self.ctx = ctx
        self.cogs = cogs
        self.current = 0
    
    
    @staticmethod
    def default_help(ctx, cogs):
        embed = discord.Embed(description = f"<:Earrow:1127175875549462602> My prefix for this server is `{tools.get_prefix(ctx.bot, ctx.message) or None}`\n<:Earrow:1127175875549462602> Total commands: `{len(ctx.bot.commands)}`\n<:Earrow:1127175875549462602> [Invite {ctx.me.name}]({discord.utils.oauth_url(ctx.me.id, permissions=discord.Permissions(permissions=1513962695871))}) | [Support Server]({ctx.bot.server}) | [Wiki]({ctx.bot.wiki})\n<:Earrow:1127175875549462602> Use `{ctx.prefix}help <command>` for more information on a command.", color=discord.Colour.dark_theme())
        embed.set_author(name=f"{ctx.me.name} help panel", icon_url=ctx.me.display_avatar.url)
        embed.add_field(name="Command Categories", value='\n'.join(f'{cog.emoji} {cog.qualified_name}' for cog in cogs), inline=False)
        embed.set_thumbnail(url=ctx.me.display_avatar.url)
        embed.set_footer(text=f"Made with ❤️ by {ctx.bot.application.owner.name}")
        return embed
    
    @staticmethod
    def cog_help(ctx, cog, page=""):
        embed = discord.Embed(color=ctx.bot.color)
        embed.set_author(name=f"{cog.qualified_name} Commands", icon_url=ctx.me.display_avatar.url)
        embed.set_thumbnail(url=ctx.me.display_avatar.url)
        embed.set_footer(text=f"Made with ❤️ by {ctx.bot.application.owner.name}{page}")
        for command in cog.walk_commands():
            embed.add_field(name=command.qualified_name, value=command.description or "None", inline=False)
        return embed
    
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            
        await interaction.response.defer()
        
        for cog in self.cogs:
            if cog.qualified_name == interaction.data["values"][0]:
                self.current = self.cogs.index(cog) + 1
                em = self.cog_help(self.ctx, cog, f" | {self.current}/{len(self.cogs)}")
                if self.current == len(self.cogs):
                    self.view.children[0].disabled = False
                    self.view.children[1].disabled = False
                    self.view.children[3].disabled = True
                    self.view.children[4].disabled = True
                else:
                    self.view.children[0].disabled = False
                    self.view.children[1].disabled = False
                    self.view.children[3].disabled = False
                    self.view.children[4].disabled = False
                return await interaction.message.edit(embed=em, view=self.view)
            elif interaction.data["values"][0] == "Home":
                em = self.default_help(self.ctx, self.cogs)
                self.current = 0
                self.view.children[0].disabled = True
                self.view.children[1].disabled = True
                self.view.children[3].disabled = False
                self.view.children[4].disabled = False
                return await interaction.message.edit(embed=em, view=self.view)
            
    
    

class Controller(View):
    def __init__(self, ctx, options, cogs):
        super().__init__(
        timeout = 120
        )
        self.ctx = ctx
        self.message = None
        self.menu = Menu(options, self.ctx, cogs)
        self.cogs = self.menu.cogs
        self.add_item(self.menu)
    
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            return False
        else:
            return True
    
    
    async def on_timeout(self):
        for children in self.children:
            if not (hasattr(children, "label") and children.label):
                children.disabled = True
        await self.message.edit(view=self)
    
    
    def set_view(self):
        if self.menu.current == 0:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[3].disabled = False
            self.children[4].disabled = False
        elif self.menu.current == len(self.menu.options)-1:
            self.children[0].disabled = False
            self.children[1].disabled = False
            self.children[3].disabled = True
            self.children[4].disabled = True
        else:
            self.children[0].disabled = False
            self.children[1].disabled = False
            self.children[3].disabled = False
            self.children[4].disabled = False
    
    
    @discord.ui.button(emoji="<:Edoublearrow2:1180724072678694962>", disabled=True)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.menu.current = 0
        self.set_view()
        em = Menu.default_help(self.ctx, self.cogs)
        return await interaction.message.edit(embed=em, view=self)
        
    
    
    @discord.ui.button(emoji="<:Earrow2:1180723707279315057>", disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.menu.current -= 1
        self.set_view()
        if self.menu.current > 0:
            em = Menu.cog_help(self.ctx, self.cogs[self.menu.current - 1], f" | {self.menu.current}/{len(self.cogs)}")
        else:
            em = Menu.default_help(self.ctx, self.cogs)
        return await interaction.message.edit(embed=em, view=self)
        
    
    @discord.ui.button(emoji="<:Edelete:1158793677712392213>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.stop()
        await interaction.message.delete()
        
    
    @discord.ui.button(emoji="<:Earrow:1127175875549462602>")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.menu.current += 1
        self.set_view()
        em = Menu.cog_help(self.ctx, self.cogs[self.menu.current - 1], f" | {self.menu.current}/{len(self.cogs)}")
        return await interaction.message.edit(embed=em, view=self)
    
    
    @discord.ui.button(emoji="<:Edoublearrow:1180723248388902933>")
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.menu.current = len(self.menu.options) - 1
        self.set_view()
        em = Menu.cog_help(self.ctx, self.cogs[self.menu.current - 1], f" | {self.menu.current}/{len(self.cogs)}")
        return await interaction.message.edit(embed=em, view=self)




class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.emoji = "<:Ebook:1127301294399426610>"
        self.invite = discord.utils.oauth_url(self.client.user.id, permissions=discord.Permissions(permissions=1513962695871))
        self.owner = self.client.application.owner
    
    
    def command_help(self, ctx, command):
        embed = discord.Embed(color=discord.Colour.dark_theme())
        embed.set_author(name=f"{command} command", icon_url=ctx.me.display_avatar.url)
        embed.add_field(name="<:Eonline:1137355060645466153> Instructions", value=">>> Required: `<>`\nOptional: `[]`\nDo not type this when using commands.", inline=False)
        embed.add_field(name="<:Eidle:1137355053666144286> Usage", value=f"> `{ctx.prefix}{command.usage}`", inline=False)
        embed.add_field(name="<:Ednd:1137355047752187944> Aliases", value=f"> `{', '.join(a for a in command.aliases) or 'None'}`", inline=False)
        embed.add_field(name="<:Einvisible:1137354444917456906> Description", value=f"> `{command.description}`", inline=False)
        embed.set_footer(text=f"Made with ❤️ by {self.owner.name}")
        return embed
    
    
    @commands.hybrid_command(name="help", description="Display commands list.", usage="help [command]")
    @app_commands.describe(command_name="Name of the command.")
    @app_commands.rename(command_name="command")
    async def help(self, ctx, *, command_name = None):
        view = View()
        if command_name:
            command = self.client.get_command(command_name.lower())
            cog = self.client.get_cog(command_name.capitalize())
            if not command and not cog:
                return await ctx.send(f"{self.client.fail} | No command/module called `{command_name}` found!", mention_author=False)
            elif command:
                em = self.command_help(ctx, command)
            elif cog:
                em = Menu.cog_help(ctx, cog)
        
        else:
            cogs = [cog for cog in self.client.cogs.values() if [command for command in cog.walk_commands()]]
            options = [discord.SelectOption(label="Home", emoji="<:Ehome:1127975367345442816>")] + [discord.SelectOption(label=cog.qualified_name, emoji=cog.emoji) for cog in cogs]
            view = Controller(ctx, options, cogs)
            em = Menu.default_help(ctx, cogs)
        
        view.add_item(Button(label="Invite Me", url=self.invite))
        view.add_item(Button(label="Support server", url=self.client.server))
        view.add_item(Button(label="Wiki", url=self.client.wiki))
        
        message = await ctx.send(embed=em, view=view)
        if not command_name: view.message = message


async def setup(client):
    await client.add_cog(Help(client))