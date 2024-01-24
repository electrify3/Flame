import json
import random
import sqlite3
import aiohttp
import discord
import datetime
from utils.config import tenor


async def get_gif(search, limit=50):
	async with aiohttp.ClientSession() as session:
		url = f"https://tenor.googleapis.com/v2/search?q={search}&key={tenor}&limit={limit}"
		async with session.get(url) as response:
			data = await response.json()
	urls = [result["media_formats"]["gif"]["url"] for result in data["results"]]
	return random.choice(urls)


def find_role(ctx, rawstr):
	restricted_characters = ["@", "&", "<", ">"]
	name = rawstr.lower().replace(" ", "")
	for c in restricted_characters:
		name = name.replace(c, "")
	try :
		role = discord.utils.get(ctx.guild.roles, id = int(name))
	except :
		role = None
	if not role:
		for i in ctx.guild.roles :
			rname = i.name.lower().replace(" ", "")
			for c in restricted_characters:
				rname = rname.replace(c, "")
			if name in rname:
				role = i
				break
	return role


def get_prefix(client, message):
	db = sqlite3.connect("data/database/Configs.db")
	c = db.cursor()
	c.execute(f'''SELECT Prefix, "No prefix" FROM Configs WHERE Guild = {message.guild.id}''')
	data = c.fetchone()
	prefix, status = data[0], data[1]
	db.close()
	if status: return ""
	else: return prefix


async def assignable(ctx, role, interaction:bool=False, client=None):
	if interaction: ctx = await client.get_context(ctx)
	if not role.is_assignable():
		embed = discord.Embed(title="Failed", description=f"My Logic says that {role.mention} is not assignable by me.", color=discord.Colour.red())
		await ctx.send(embed=embed)
		return False
	else:
		return True


def get_afk():
	with open("data/afks.json", "r") as f:
		data = json.load(f)
	return data


def remove_afk(user):
	data = get_afk()
	data[str(user.id)]["time"] = None
	data[str(user.id)]["message"] = None
	with open("data/afks.json","w") as f :
		json.dump(data, f)



def setup_afk(user):
	data = get_afk()
	if str(user.id) in data :
		return False
	else :
		data[str(user.id)] = {}
		data[str(user.id)]["time"] = None
		data[str(user.id)]["message"] = None
		with open("data/afks.json","w") as f :
			json.dump(data, f)
		return True

def add_afk(user, message) :
	data = get_afk()
	data[str(user.id)]["time"] = datetime.datetime.utcnow().timestamp()
	data[str(user.id)]["message"] = message
	with open("data/afks.json","w") as f :
		json.dump(data, f)




async def check_position(ctx, role, interaction:bool=False, client=None):
	if interaction: ctx = await client.get_context(ctx)
	if role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
		embed = discord.Embed(title="Failed", description=f"You don't have enough permissions to manage {role.mention}.", color=discord.Colour.red())
		await ctx.send(embed=embed)
		return False
	else: return True

async def editable(ctx, role, interaction=False, client=None):
	if interaction: ctx = await client.get_context(ctx)
	if role.position >= ctx.guild.me.top_role.position:
		embed = discord.Embed(title="Failed", description=f"I don't have enough permissions to manage {role.mention}.", color= discord.Colour.red())
		await ctx.send(embed=embed)
		return False
	else: return True


async def addable(ctx, role, interaction:bool=False, client=None):
	if interaction: ctx = await client.get_context(ctx)
	if not await check_position(ctx, role): return False
	if not await assignable(ctx, role): return False
	else: return True


async def is_banned(ctx, user):
	status = False
	async for ban in ctx.guild.bans(limit=None):
		if user.id == ban.user.id:
			status = True
	return status




def format_time(raw_string):
	
	def clean_string(raw_string):
		raw_string = raw_string.replace("years", "y")
		raw_string = raw_string.replace("yrs", "y")
		raw_string = raw_string.replace("months", "M")
		raw_string = raw_string.replace("month", "M")
		raw_string = raw_string.replace("mon", "M")
		raw_string = raw_string.replace("weeks", "w")
		raw_string = raw_string.replace("days", "d")
		raw_string = raw_string.replace("hours", "h")
		raw_string = raw_string.replace("hrs", "h")
		raw_string = raw_string.replace("minutes", "m")
		raw_string = raw_string.replace("mins", "m")
		raw_string = raw_string.replace("seconds", "s")
		raw_string = raw_string.replace("secs", "s")
		return raw_string
	
	raw_string = clean_string(raw_string)
	
	helper_string = ""
	time_value = []
	time_unit = []

	for i in range(len(raw_string)):
		try:
			int(raw_string[i])
			helper_string += raw_string[i]
			
		except:
			if len(helper_string) != 0:
				helper_string = helper_string.split()
				for j in helper_string:
					time_value.append(j)
				helper_string = ""
				
			if raw_string[i] == "y":
				time_unit.append(raw_string[i])
			if raw_string[i] == "M":
				time_unit.append(raw_string[i])
			if raw_string[i] == "w":
				time_unit.append(raw_string[i])
			if raw_string[i] == "d":
				time_unit.append(raw_string[i])
			if raw_string[i] == "h":
				time_unit.append(raw_string[i])
			if raw_string[i] == "m":
				time_unit.append(raw_string[i])
			if raw_string[i] == "s":
				time_unit.append(raw_string[i])
		
	if len(helper_string) != 0:
		helper_string = helper_string.split()
		for j in helper_string:
			time_value.append(j)
		helper_string = ""
		
	weeks = 0
	days = 0
	hours = 0
	minutes = 0
	seconds = 0
	
	for id in range(len(time_value)):
		try :
			if time_unit[id] == "y":
				days += int(time_value[id])*365
			if time_unit[id] == "M":
				days += int(time_value[id])*30
			if time_unit[id] == "w":
				weeks = int(time_value[id])
			if time_unit[id] == "d":
				days += int(time_value[id])
			if time_unit[id] == "h":
				hours = int(time_value[id])
			if time_unit[id] == "m":
				minutes = int(time_value[id])
			if time_unit[id] == "s":
				seconds = int(time_value[id])
		except:
			pass
	
	if len(time_value) == 1 and len(time_unit) == 0:
		seconds += int(time_value[0])
		
	return datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)


def clean_time(seconds:int):
	duration = str(datetime.timedelta(seconds=seconds))
	exceptions = ["0", ":"]
	new_duration = ""
	
	for i in range(len(duration)):
		if duration[i] not in exceptions :
			new_duration = duration.replace(duration[:i], "")
			break
	return new_duration