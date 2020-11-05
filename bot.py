import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import CommandNotFound, CommandInvokeError
from async_timeout import timeout

TOKEN = 'NzcyODU5MzQ0NTUwNDk0MjE5.X6AzWg.rLdgR--eCLiK2d9IYztlUxOsKoA'

description = 'TechBot in Python'
bot = commands.Bot(command_prefix='>', description=description)

vc_is_paused = False

@bot.event
async def on_ready():
    print('Successfully logged in as',end=" ")
    print(bot.user.name,end=" ")
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=">help"))
    async for guild in bot.fetch_guilds():
        if guild.id == 340043063798005780:
            channel = bot.get_channel(773235560944631868)
            await channel.send("The bot is now online")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    #if isinstance(error, CommandInvokeError): # This is to stop flagging an error with the leave() command.
        #return                                # It is probably a good idea to remove it when testing a new module/command.
    raise error

@bot.command()
@commands.is_owner()
async def load(ctx,extension):
    bot.load_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Load",value="✅ Successfully loaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar,delete_after=5)

@bot.command()
@commands.is_owner()
async def unload(ctx,extension):
    bot.unload_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Unload",value="✅ Successfully unloaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar,delete_after=5)

@bot.command()
@commands.is_owner()
async def reload(ctx,extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Reload",value="✅ Successfully reloaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar,delete_after=5)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)