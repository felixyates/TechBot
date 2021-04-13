import discord, os, asyncio, sqlite3
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import CommandNotFound
from async_timeout import timeout
from modules.emoji import yep,nope,tada_animated
from modules.embedvars import setembedvar

with open('/home/felixyates1/token.txt','r') as file:
    file = file.readlines()
    TOKEN = str(file[0])

description = 'TechBot in Python'
intents = discord.Intents().all()
intents.voice_states = True
bot = commands.Bot(command_prefix='>', description=description, intents = intents)

vc_is_paused = False

@bot.event
async def on_ready():
    print('Successfully logged in as',end=" ")
    print(bot.user.name,end=" ")
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for >help"))
    async for guild in bot.fetch_guilds():
        if guild.id == 788802564912709692:
            channel = bot.get_channel(788802645070053377)
            onlineVar = setembedvar("G","Bot Online",f"{tada_animated} TechBot is back online and reporting for duty!",False)
            await channel.send(embed = onlineVar)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.command()
@commands.is_owner()
async def load(ctx,extension):
    try:
        bot.load_extension(f'cogs.{extension}')
        embedVar = setembedvar("G","Successful Load",f"{yep} Successfully loaded "+ extension,False)
        await ctx.message.channel.send(embed=embedVar)
    except:
        embedVar = setembedvar("R","Unsuccessful Load",f"{nope} Couldn't load "+ extension,False)
        await ctx.message.channel.send(embed=embedVar)

@bot.command()
@commands.is_owner()
async def unload(ctx,extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        embedVar = setembedvar("G","Successful Unload",f"{yep} Successfully unloaded "+ extension,False)
        await ctx.message.channel.send(embed=embedVar)
    except:
        embedVar = setembedvar("R","Unsuccessful Unload",f"{nope} Couldn't unload "+ extension,False)
        await ctx.message.channel.send(embed=embedVar)

@bot.command()
@commands.is_owner()
async def reload(ctx,extension):
    try:
        bot.reload_extension(f'cogs.{extension}')
        embedVar = setembedvar("G","Successful Reload",f"{yep} Successfully reloaded "+ extension,False)
        await ctx.message.channel.send(embed=embedVar)
    except:
        embedVar = setembedvar("R","Unsuccessful Reload",f"{nope} Couldn't reload "+ extension,False)
        await ctx.message.channel.send(embed=embedVar)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)