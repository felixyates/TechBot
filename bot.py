import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
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
            await channel.send("The main bot module is now online 🥳")

@bot.command()
async def load(ctx,extension):
    bot.load_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Load",value="✅ Successfully loaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar)

@bot.command()
async def unload(ctx,extension):
    bot.unload_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Unload",value="✅ Successfully unloaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)