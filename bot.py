import discord, os, asyncio, random, sys
import smtplib, ssl, utils
import subprocess, time
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import CommandNotFound, CommandInvokeError
from async_timeout import timeout
from email.message import EmailMessage

with open('/home/pi/Documents/token.txt','r') as file:
    file = file.readlines()
    TOKEN = str(file[0])

with open('/home/pi/Documents/emailConfig.txt','r') as file:
    file = str(file.read()).split(',')
    host = str(file[0])
    USERNAME = str(file[1])
    PASSWORD = str(file[2])
    toaddr = str(file[3])
    fromaddr = USERNAME

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
        if guild.id == 340043063798005780:
            channel = bot.get_channel(773235560944631868)
            await channel.send("The bot is now online")
    context = ssl.create_default_context()
    msg = """\
Subject: UP

This message is sent from Python."""
    with smtplib.SMTP_SSL('techlifeyt.com', 465, context=context) as server:
        server.login(USERNAME, PASSWORD)
        server.sendmail(fromaddr, toaddr, msg)
        print('Sent status email successfully.')

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
    await ctx.message.channel.send(embed=embedVar)

@bot.command()
@commands.is_owner()
async def unload(ctx,extension):
    bot.unload_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Unload",value="✅ Successfully unloaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar)

@bot.command()
@commands.is_owner()
async def reload(ctx,extension):
    bot.reload_extension(f'cogs.{extension}')
    embedVar = discord.Embed(color=0x00ff00)
    embedVar.add_field(name="Successful Reload",value="✅ Successfully reloaded "+ extension, inline=False)
    await ctx.message.channel.send(embed=embedVar)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != 'troll.py':
        bot.load_extension(f'cogs.{filename[:-3]}')

""" @bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.message.add_reaction('✅')
    await bot.clear()
    await bot.logout()
    cmd = 'python3 bot.py'
    subprocess.run(cmd, shell=True)   
    time.sleep(0.2)
    quit() """

bot.run(TOKEN)