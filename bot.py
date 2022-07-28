import discord, os
from discord.ext import commands
from modules import getjson

TOKEN = getjson.secret("discord")
intents = discord.Intents().all()
bot = commands.Bot(intents = intents)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)