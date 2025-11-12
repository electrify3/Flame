import random
import datetime

import aiohttp
import discord

from discord import app_commands
from discord.ext import commands
from discord.ui import View

from utils import tools


class TruthDare(View):
    def __init__(self):
        super().__init__()
        self.user = None
        self.message = None
    
    
    async def on_timeout(self):
        for component in self.children:
            component.disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message(f"{interaction.bot.warning} | You don't own this session!", ephemeral=True)
            return False
        else:
            return True
    
    @discord.ui.button(label='Truth', style=discord.ButtonStyle.green)
    async def send_truth(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/truth") as response:
                question = (await response.json())["question"]
        
        em = discord.Embed(title="Truth", description=question, color=discord.Colour.green(), timestamp=datetime.datetime.now(datetime.UTC))
        em.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        view = TruthDare()
        view.user = interaction.user
        await interaction.message.edit(view=None)
        view.message = await interaction.followup.send(embed=em, view=view)
        self.stop()
        
    @discord.ui.button(label='Dare', style=discord.ButtonStyle.red)
    async def send_dare(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/dare") as response:
                question = (await response.json())["question"]
        
        em = discord.Embed(title="Dare", description=question, color=discord.Colour.red(), timestamp=datetime.datetime.now(datetime.UTC))
        em.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        view = TruthDare()
        view.user = interaction.user
        await interaction.message.edit(view=None)
        view.message = await interaction.followup.send(embed=em, view=view)
        self.stop()
    
    @discord.ui.button(label='Random', style=discord.ButtonStyle.blurple)
    async def send_random(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        choice = random.choice(['truth', 'dare'])
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.truthordarebot.xyz/v1/{choice}") as response:
                question = (await response.json())["question"]
        
        em = discord.Embed(title=choice.title(), description=question, color=discord.Colour.blurple(), timestamp=datetime.datetime.now(datetime.UTC))
        em.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        view = TruthDare()
        view.user = interaction.user
        await interaction.message.edit(view=None)
        view.message = await interaction.followup.send(embed=em, view=view)
        self.stop()


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = "<:Egame:1127303566768488508>"
    
    @commands.hybrid_command(name="roll", description="Rolls a dice.", aliases=["dice"], usage="roll [limit]")
    @commands.guild_only()
    @app_commands.describe(limit="Range of the dice.")
    async def roll(self, ctx, limit = 6):
        value = random.randint(1, limit)
        await ctx.send(f'{ctx.author.mention} rolled: **{value}** ||(1-{limit})||')
    
    @commands.hybrid_command(name="coinflip", description="Flips a coin.", aliases=["cf"], usage="coinflip")
    @commands.guild_only()
    async def coinflip(self, ctx):
        possibilities = ["Head!","Tail!"]
        result = random.choice(possibilities)
        await ctx.send(f'{ctx.author.mention} flipped a coin: **{result}**')
    
    @commands.hybrid_command(name="kiss", description="Kisses a user.", usage="kiss <member>")
    @commands.guild_only()
    @app_commands.describe(user="User you want to kiss.")
    async def kiss(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = await tools.get_gif("anime kiss")
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{ctx.author.name} kissed {user.name}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    @commands.hybrid_command(name="cuddle", description="Cuddles a user.", usage="cuddle <member>", aliases=["hug"])
    @commands.guild_only()
    @app_commands.describe(user="User you want to cuddle.")
    async def cuddle(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = await tools.get_gif("anime hug")
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{ctx.author.name} cuddled {user.name}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    @commands.hybrid_command(name="slap", description="Slaps a user.", usage="slap <member>")
    @commands.guild_only()
    @app_commands.describe(user="User you want to slap.")
    async def slap(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = await tools.get_gif("anime slap")
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{ctx.author.name} slapped {user.name}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    @commands.hybrid_command(name="kill", description="Kills a user.", usage="kill <member>")
    @commands.guild_only()
    @app_commands.describe(user="User you want to kill.")
    async def kill(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = await tools.get_gif("anime wasted", 20)
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{ctx.author.name} killed {user.name}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    @commands.hybrid_command(name="bully", description="Bullies a user.", usage="bully <member>")
    @commands.guild_only()
    @app_commands.describe(user="User you want to bully.")
    async def bully(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = await tools.get_gif("anime bully")
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{ctx.author.name} bullied {user.name}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    @commands.hybrid_command(name="bite", description="bitess a user.", usage="kill <member>")
    @commands.guild_only()
    @app_commands.describe(user="User you want to bite.")
    async def bite(self, ctx, user: discord.Member):
        await ctx.defer()
        gif = await tools.get_gif("anime bite", 20)
        em = discord.Embed(color=self.bot.color)
        em.set_author(name=f"{ctx.author.name} bitten {user.name}", icon_url=ctx.author.display_avatar.url)
        em.set_image(url=gif)
        await ctx.send(f"{user.mention}",embed=em)
    
    @commands.hybrid_command(name="thanos", description="Sends a Thanos quote.", usage="thanos")
    @commands.guild_only()
    async def thanos(self, ctx):
        await ctx.defer()
        gif = await tools.get_gif("thanos quote", 20)
        em = discord.Embed(color=self.bot.color)
        em.set_image(url=gif)
        await ctx.send(f"{ctx.author.mention}",embed=em)
    
    
    @commands.hybrid_command(name="enlarge", description="Enlarge a emoji.", usage="enlarge <emoji>")
    @commands.guild_only()
    @app_commands.describe(emoji="Emoji you want to enlarge.")
    async def enlarge(self, ctx, emoji: discord.PartialEmoji):
        em = discord.Embed(title="Enlarged emoji", color=self.bot.color)
        em.set_image(url=emoji.url)
        em.set_footer(text=f"Request by {ctx.author}.")
        await ctx.send(embed=em)
    
    
    @commands.hybrid_command(name="truth", description="Gives a truth question.", usage="truth")
    @commands.guild_only()
    async def truth(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/truth") as response:
                question = (await response.json())["question"]
        em = discord.Embed(title="Truth", description=question, color=discord.Colour.green(), timestamp=datetime.datetime.now(datetime.UTC))
        em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = TruthDare()
        view.user = ctx.author
        view.message = await ctx.send(embed=em, view=view)
    
    
    @commands.hybrid_command(name="dare", description="Gives a dare question.", usage="dare")
    @commands.guild_only()
    async def dare(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/dare") as response:
                question = (await response.json())["question"]
        em = discord.Embed(title="Dare", description=question, color=discord.Colour.red(), timestamp=datetime.datetime.now(datetime.UTC))
        em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = TruthDare()
        view.user = ctx.author
        view.message = await ctx.send(embed=em, view=view)


async def setup(bot):
    await bot.add_cog(Fun(bot))