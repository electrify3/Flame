import os

import dotenv

from discord import Colour

prefix = "??"

dotenv.load_dotenv()
token = os.environ['TOKEN']
tenor = os.environ['TENOR']

wiki = "https://github.com/electrify3/Flame/wiki"
server = "https://discord.gg/gsug3senpe"

success = "<:Esuccess:1134146893383991466>"
warning = "<:Ewarning:1134146899482513438>"
fail = "<:Efail:1134146887541338132>"
working = "<a:Eworking:1134706784540569650>"

admins = [657542394576764938, 712933514684661781]
color = Colour.blurple()
badges = {} # Coming soon