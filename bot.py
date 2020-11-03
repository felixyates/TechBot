import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio
#import youtube_dl
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
async def hello(ctx):
    "Says 'world'"
    await ctx.send("world")

@bot.command()
async def add(ctx, left : int, right : int):
    "Adds two numbers together."
    await ctx.send(left + right)

@bot.command()
async def servers(ctx):
    "Lists some cool beans servers you should join"
    await ctx.send("- gaming (#1): https://discord.gg/wWdr9bf\n- gaming (#2): https://discord.gg/bZFFgXnAVZ")

@bot.command()
async def ping(ctx):
    "Returns 'pong' if the bot is active"
    await ctx.send("pong")

@bot.command()
async def leave(ctx):
    "Leave a voice channel"
    await ctx.voice_client.disconnect()

@bot.command(pass_context=True)
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.User=None):
    "Simple kick command"
    await ctx.guild.kick(member)
    kickMessage = "Successfully kicked" ,str(member)
    await ctx.channel.send("Successfully kicked" ,str(kickMessage))
    print("Successfully kicked" + " " + str(member))

@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.User=None):
    "Simple ban command"
    await ctx.guild.ban(member)
    banMessage = "Successfully banned" ,str(member)
    await ctx.channel.send(banMessage)
    print("Successfully banned" + " " + str(member))

@bot.command(pass_context=True)
async def fnaf(ctx):
    "Plays the FNAF phone call in the voice channel"
    # grab the user who sent the command
    user = ctx.message.author
    channel = user.voice.channel
    if channel!= None:
        # grab user's voice channel
        channelName=channel.name
        await ctx.channel.send('@'+str(user)+' is in channel: '+ channelName)
        # create StreamPlayer
        global vc
        vc= await channel.connect()
        vc.play(discord.FFmpegPCMAudio('fnaf.mp3'), after=lambda e: print('done', e))
        while vc.is_playing() == True:
            await asyncio.sleep(1)
        # disconnect after the player has finished
        vc.stop()
        await leave(ctx)
    else:
        await ctx.channel.send("Join a channel first.")
        await ctx.channel.send(user).format(ctx.message.author.mention())

@bot.command(pass_context=True)
async def stop(ctx):
    "Stops the currently playing audio in voice chat"
    if vc.is_playing() == True:
        vc.stop()
        await leave(ctx)
        vc_is_paused == False
        await ctx.channel.send("Stopped!")
    else:
        await ctx.channel.send("Nothing is playing!")

@bot.command(pass_context=True)
@has_permissions(manage_messages=True)
async def purge(ctx):
    "Deletes a specied number of messages (max 100).\nOnly works for messages under 14 days old, and you must have the 'Manage Messages' permission."
    channel = ctx.channel
    msg = str(ctx.message.content)
    print(msg)
    msgList = msg.split( )
    print(msgList)
    deleteNo = int(msgList[1])
    print(deleteNo)
    async with channel.typing():
        await message.delete_messages(deleteNo)
        await ctx.channel.send("Deleted "+ deleteNo +" messages.",delete_after="5")

# @bot.command(pass_context=True)
# async def pause(ctx):
#     "Pauses the currently playing audio in voice chat"
#     if vc.is_playing() == True:
#         vc.pause()
#         await ctx.channel.send("Paused!")
#         global vc_is_paused
#         vc_is_paused = True
#     else:
#         await ctx.channel.send("Nothing is playing!")

# @bot.command(pass_context=True)
# async def resume(ctx):
#     "Resumes the currently playing audio in voice chat"
#     if vc_is_paused == True:
#         vc.resume()
#         while vc.is_playing() != True:
#             await asyncio.sleep(1)
#         await ctx.channel.send("Resumed!")
#     else:
#         await ctx.channel.send("Nothing is playing!")

bot.run(TOKEN)