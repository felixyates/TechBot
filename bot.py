import discord, os
from discord.ext import commands
from modules.getjson import secret, get_prefix
from discord_slash import SlashCommand

TOKEN = secret("discord")

intents = discord.Intents().all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=get_prefix, intents = intents)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)