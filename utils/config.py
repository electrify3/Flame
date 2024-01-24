import os
import discord

prefix = "?"

token = os.environ["Token"]
openai = os.environ["OpenAI"]
tenor = os.environ["TenorKey"]

wiki = "https://github.com/electrify3"
server = "https://discord.gg/gsug3senpe"

success = "<:Esuccess:1134146893383991466>"
warning = "<:Ewarning:1134146899482513438>"
fail = "<:Efail:1134146887541338132>"
working = "<a:Eworking:1134706784540569650>"

admins = [657542394576764938, 723913737043574824]

color = discord.Colour.green()
badges = {}