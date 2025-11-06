import datetime
import json
import random
import re

import aiohttp
import aiosqlite
import discord

from discord.ext import commands

from utils.config import tenor


async def get_gif(search: str, limit: int = 50) -> str:
    async with aiohttp.ClientSession() as session:
        url = f"https://tenor.googleapis.com/v2/search?q={search}&key={tenor}&limit={limit}"
        async with session.get(url) as response:
            data = await response.json()
    urls = [result["media_formats"]["gif"]["url"] for result in data["results"]]
    return random.choice(urls)


def find_role(ctx: commands.Context, rawstr: str) -> discord.Role | None:
    restricted_characters = {"@", "&", "<", ">"}
    name = "".join(c for c in rawstr if c not in restricted_characters).lower().replace(" ", "")
    try :
        return discord.utils.get(ctx.guild.roles, id = int(name))
    except ValueError:
        for role in ctx.guild.roles:
            rname = "".join(c for c in role.name if c not in restricted_characters).lower().replace(" ", "")
            if name in rname:
                return role
    return None


async def get_prefix(client: discord.Client, message: discord.Message) -> str:
    async with aiosqlite.connect('data/database/Configs.db') as db:
        async with db.execute(f'''SELECT Prefix, "No prefix" FROM Configs WHERE Guild = {message.guild.id}''') as c:
            data = await c.fetchone()
            prefix, status = data[0], data[1]
            if status:
                prefix = ""
    return prefix

def get_afk() -> dict:
    with open("data/afks.json", "r") as f:
        data = json.load(f)
    return data

def remove_afk(user: discord.Member) -> None:
    data = get_afk()
    data[str(user.id)]["time"] = None
    data[str(user.id)]["message"] = None
    with open("data/afks.json","w") as f :
        json.dump(data, f)

def setup_afk(user: discord.Member) -> bool:
    data = get_afk()
    if str(user.id) in data:
        return False
    else :
        data[str(user.id)] = {}
        data[str(user.id)]["time"] = None
        data[str(user.id)]["message"] = None
        with open("data/afks.json","w") as f :
            json.dump(data, f)
        return True

def add_afk(user: discord.Member, message: str) -> None:
    data = get_afk()
    data[str(user.id)]["time"] = datetime.datetime.now(datetime.timezone.utc).timestamp()
    data[str(user.id)]["message"] = message
    with open("data/afks.json","w") as f :
        json.dump(data, f)


async def is_assignable(ctx: commands.Context, role: discord.Role) -> bool:
    if not role.is_assignable():
        embed = discord.Embed(title="Failed", description=f"{role.mention} is not assignable by me.", color=discord.Colour.red())
        await ctx.send(embed=embed)
        return False
    return True

async def has_position(ctx: commands.Context, role: discord.Role) -> bool:
    if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
        embed = discord.Embed(title="Failed", description=f"You don't have enough permissions to manage {role.mention}.", color=discord.Colour.red())
        await ctx.send(embed=embed)
        return False
    return True

async def is_editable(ctx: commands.Context, role: discord.Role) -> bool:
    if role.position >= ctx.guild.me.top_role.position:
        embed = discord.Embed(title="Failed", description=f"I don't have enough permissions to manage {role.mention}.", color= discord.Colour.red())
        await ctx.send(embed=embed)
        return False
    return True


async def is_addable(ctx: commands.Context, role: discord.Role) -> bool:
    if await has_position(ctx, role) and await is_assignable(ctx, role):
        return True
    return False


async def is_banned(ctx: commands.Context, user: discord.User) -> bool:
    async for ban in ctx.guild.bans(limit=None):
        if user.id == ban.user.id:
            return True
    return False



def format_time(raw_string: str) -> datetime.timedelta:
    replacements = {
        r"\b(years?|yrs?)\b": "y",
        r"\b(months?|mon)\b": "M",
        r"\b(weeks?)\b": "w",
        r"\b(days?)\b": "d",
        r"\b(hours?|hrs?)\b": "h",
        r"\b(minutes?|mins?)\b": "m",
        r"\b(seconds?|secs?)\b": "s"
    }

    for pattern in replacements:
        raw_string = re.sub(pattern, replacements[pattern], raw_string, flags=re.IGNORECASE)

    matches = re.findall(r"(\d+)([yMwDdhms])?", raw_string)

    unit_map = {
        "y": ("days", 365),
        "M": ("days", 30),
        "w": ("weeks", 1),
        "d": ("days", 1),
        "h": ("hours", 1),
        "m": ("minutes", 1),
        "s": ("seconds", 1),
        None: ("seconds", 1)
    }

    time_data = {"weeks": 0, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}

    for value, unit in matches:
        key, multiplier = unit_map[unit]
        time_data[key] += int(value) * multiplier

    return datetime.timedelta(**time_data)


def clean_time(seconds: int) -> str:
    duration = str(datetime.timedelta(seconds=seconds))
    return duration.lstrip("0:") or "0"