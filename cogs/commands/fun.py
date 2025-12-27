import random
import datetime
import typing

import aiohttp
import discord

from discord import app_commands
from discord.ext import commands
from discord.ui import View

from utils import tools

if typing.TYPE_CHECKING:
    from main import Bot


class TruthDare(View):

    def __init__(self, author: discord.Member) -> None:
        super().__init__()
        self.author: discord.Member = author
        self.message: discord.Message | None = None
    
    
    async def on_timeout(self) -> None:
        for component in self.children:
            component.disabled = True

        await self.message.edit(view=self)
    

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message(f"{interaction.client.warning} | You don't own this session!", ephemeral=True)
            return False
        
        else:
            return True
    

    @discord.ui.button(label='Truth', style=discord.ButtonStyle.green)
    async def send_truth(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/truth") as response:
                question = (await response.json())["question"]
        
        embed = discord.Embed(title="Truth", description=question, color=discord.Colour.green(), timestamp=datetime.datetime.now(datetime.UTC))
        embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)

        view = TruthDare()
        view.author = interaction.user

        await interaction.message.edit(view=None)
        view.message = await interaction.followup.send(embed=embed, view=view)
        self.stop()
    

    @discord.ui.button(label='Dare', style=discord.ButtonStyle.red)
    async def send_dare(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/dare") as response:
                question = (await response.json())["question"]
        
        embed = discord.Embed(title="Dare", description=question, color=discord.Colour.red(), timestamp=datetime.datetime.now(datetime.UTC))
        embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)

        view = TruthDare()
        view.author = interaction.user

        await interaction.message.edit(view=None)
        view.message = await interaction.followup.send(embed=embed, view=view)
        self.stop()
    

    @discord.ui.button(label='Random', style=discord.ButtonStyle.blurple)
    async def send_random(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        choice = random.choice(['truth', 'dare'])

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.truthordarebot.xyz/v1/{choice}") as response:
                question = (await response.json())["question"]
        
        embed = discord.Embed(title=choice.title(), description=question, color=discord.Colour.blurple(), timestamp=datetime.datetime.now(datetime.UTC))
        embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)

        view = TruthDare()
        view.author = interaction.user

        await interaction.message.edit(view=None)
        view.message = await interaction.followup.send(embed=embed, view=view)
        self.stop()


class Fun(commands.Cog):

    def __init__(self, bot: 'Bot') -> None:
        self.bot: Bot = bot
        self.emoji: str = "<:Egame:1127303566768488508>"
    

    def make_embed(self, action: str, author: discord.Member, target: discord.Member, url: str) -> discord.Embed:
        embed = discord.Embed(color=self.bot.color)
        embed.set_author(name=f"{author.name} {action} {target.name}", icon_url=author.display_avatar.url)
        embed.set_image(url=url)
        return embed


    @commands.hybrid_command(name="roll", description="Rolls a dice.", aliases=["dice"], usage="roll [limit]")
    @commands.guild_only()
    @app_commands.describe(limit="Range of the dice.")
    async def roll(self, ctx: commands.Context, limit: int = 6) -> None:
        value = random.randint(1, limit)
        await ctx.send(f'{ctx.author.mention} rolled: **{value}** ||(1-{limit})||')
    

    @commands.hybrid_command(name="coinflip", description="Flips a coin.", aliases=["cf"], usage="coinflip")
    @commands.guild_only()
    async def coinflip(self, ctx: commands.Context) -> None:
        possibilities = ["Head!","Tail!"]
        result = random.choice(possibilities)
        await ctx.send(f'{ctx.author.mention} flipped a coin: **{result}**')
    

    @commands.hybrid_command(name="kiss", description="Kisses a user.", usage="kiss <member>")
    @commands.guild_only()
    @app_commands.describe(member="User you want to kiss.")
    async def kiss(self, ctx: commands.Context, member: discord.Member) -> None:
        url = await tools.get_gif("anime kiss")
        embed = self.make_embed('kissed', ctx.author, member, url)
        await ctx.send(member.mention, embed=embed)
    

    @commands.hybrid_command(name="cuddle", description="Cuddles a user.", usage="cuddle <member>", aliases=["hug"])
    @commands.guild_only()
    @app_commands.describe(member="User you want to cuddle.")
    async def cuddle(self, ctx: commands.Context, member: discord.Member) -> None:
        url = await tools.get_gif("anime hug")
        embed = self.make_embed('cuddled', ctx.author, member, url)
        await ctx.send(member.mention, embed=embed)
    

    @commands.hybrid_command(name="slap", description="Slaps a user.", usage="slap <member>")
    @commands.guild_only()
    @app_commands.describe(member="User you want to slap.")
    async def slap(self, ctx: commands.Context, member: discord.Member) -> None:
        url = await tools.get_gif("anime slap")
        embed = self.make_embed('slapped', ctx.author, member, url)
        await ctx.send(member.mention, embed=embed)
    

    @commands.hybrid_command(name="kill", description="Kills a user.", usage="kill <member>")
    @commands.guild_only()
    @app_commands.describe(member="User you want to kill.")
    async def kill(self, ctx: commands.Context, member: discord.Member) -> None:
        url = await tools.get_gif("anime wasted", 20)
        embed = self.make_embed('killed', ctx.author, member, url)
        await ctx.send(member.mention, embed=embed)
    

    @commands.hybrid_command(name="bully", description="Bullies a user.", usage="bully <member>")
    @commands.guild_only()
    @app_commands.describe(member="User you want to bully.")
    async def bully(self, ctx: commands.Context, member: discord.Member) -> None:
        url = await tools.get_gif("anime bully")
        embed = self.make_embed('bullied', ctx.author, member, url)
        await ctx.send(member.mention, embed=embed)
    

    @commands.hybrid_command(name="bite", description="bitess a user.", usage="kill <member>")
    @commands.guild_only()
    @app_commands.describe(member="User you want to bite.")
    async def bite(self, ctx: commands.Context, member: discord.Member) -> None:
        url = await tools.get_gif("anime bite", 20)
        embed = self.make_embed('bitten', ctx.author, member, url)
        await ctx.send(member.mention, embed=embed)
    

    @commands.hybrid_command(name="thanos", description="Sends a Thanos quote.", usage="thanos")
    @commands.guild_only()
    async def thanos(self, ctx: commands.Context) -> None:
        url = await tools.get_gif("thanos quote", 20)
        embed = discord.Embed(color=self.bot.color)
        embed.set_image(url=url)
        await ctx.send(ctx.author.mention, embed=embed)
    
    
    @commands.hybrid_command(name="enlarge", description="Enlarge a emoji.", usage="enlarge <emoji>")
    @commands.guild_only()
    @app_commands.describe(emoji="Emoji you want to enlarge.")
    async def enlarge(self, ctx: commands.Context, emoji: discord.PartialEmoji) -> None:
        embed = discord.Embed(title="Enlarged emoji", color=self.bot.color)
        embed.set_image(url=emoji.url)
        embed.set_footer(text=f"Request by {ctx.author}.")
        await ctx.send(embed=embed)
    
    
    @commands.hybrid_command(name="truth", description="Gives a truth question.", usage="truth")
    @commands.guild_only()
    async def truth(self, ctx: commands.Context) -> None:

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/truth") as response:
                question = (await response.json())["question"]

        embed = discord.Embed(title="Truth", description=question, color=discord.Colour.green(), timestamp=datetime.datetime.now(datetime.UTC))
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = TruthDare()
        view.user = ctx.author
        view.message = await ctx.send(embed=embed, view=view)
    
    
    @commands.hybrid_command(name="dare", description="Gives a dare question.", usage="dare")
    @commands.guild_only()
    async def dare(self, ctx: commands.Context) -> None:

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.truthordarebot.xyz/v1/dare") as response:
                question = (await response.json())["question"]

        embed = discord.Embed(title="Dare", description=question, color=discord.Colour.red(), timestamp=datetime.datetime.now(datetime.UTC))
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = TruthDare()
        view.user = ctx.author
        view.message = await ctx.send(embed=embed, view=view)


async def setup(bot: 'Bot') -> None:
    await bot.add_cog(Fun(bot))