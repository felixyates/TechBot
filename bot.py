import discord, os, asyncio, json
from discord.ext import commands, tasks
from discord.ext.tasks import loop
from asyncio import sleep
from discord.ext.commands import has_permissions
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from async_timeout import timeout
from modules.emoji import yep,nope,tada_animated
from modules.embedvars import setembedvar
from modules.getjson import secret, get_prefix

TOKEN = secret("discord")

description = 'TechBot'
intents = discord.Intents().all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=get_prefix, description=description, intents = intents)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(embed=setembedvar("R","Command Missing Argument(s)",f"`{str(error)}`"))
        return
    else:
        errorChannel = 837336145272111114 # techbot, error log
        channel = bot.get_channel(errorChannel)
        embed = setembedvar("R","An Error Occurred")
        embed.add_field(name="Guild Name", value=f"`{ctx.guild.name}`")
        embed.add_field(name="Guild ID", value=f"`{ctx.guild.id}`")
        embed.add_field(name="Channel ID", value=f"`{ctx.channel.id}`")
        embed.add_field(name="Command Issuer", value=f"`{ctx.author.name} // {ctx.author.id}`")
        embed.add_field(name="Message", value=f"`{ctx.message.content}`")
        embed.add_field(name="Error Contents", value=f"`{str(error)}`", inline=False)
        await channel.send(embed=embed)

@bot.command()
@commands.is_owner()
async def load(ctx,extension):
    try:
        bot.load_extension(f'cogs.{extension}')
        embedVar = setembedvar("G","Successful Load",f"{yep} Successfully loaded "+ extension)
        await ctx.message.channel.send(embed=embedVar)
    except Exception as e:
        embedVar = setembedvar("R","Unsuccessful Load",f"{nope} Couldn't load "+ extension+ "\n"+f"`{e}`")
        await ctx.message.channel.send(embed=embedVar)

@bot.command()
@commands.is_owner()
async def unload(ctx,extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        embedVar = setembedvar("G","Successful Unload",f"{yep} Successfully unloaded "+ extension)
        await ctx.message.channel.send(embed=embedVar)
    except Exception as e:
        embedVar = setembedvar("R","Unsuccessful Unload",f"{nope} Couldn't unload "+ extension+ "\n"+f"`{e}`")
        await ctx.message.channel.send(embed=embedVar)

@bot.command()
@commands.is_owner()
async def reload(ctx,extension):
    try:
        bot.reload_extension(f'cogs.{extension}')
        embedVar = setembedvar("G","Successful Reload",f"{yep} Successfully reloaded "+ extension)
        await ctx.message.channel.send(embed=embedVar)
    except Exception as e:
        embedVar = setembedvar("R","Unsuccessful Reload",f"{nope} Couldn't reload "+ extension+ "\n"+f"`{e}`")
        await ctx.message.channel.send(embed=embedVar)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)