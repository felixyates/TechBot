import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

TOKEN = 'NzcyODU5MzQ0NTUwNDk0MjE5.X6AzWg.rLdgR--eCLiK2d9IYztlUxOsKoA'

description = '''TechBot in Python'''
bot = commands.Bot(command_prefix='>', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def hello(ctx):
    """Says 'world'"""
    await ctx.send("world")

@bot.command()
async def add(ctx, left : int, right : int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def servers(ctx):
    """Lists some cool beans servers you should join"""
    await ctx.send("- gaming (#1): https://discord.gg/wWdr9bf\n- gaming (#2): https://discord.gg/bZFFgXnAVZ")

@bot.command()
async def ping(ctx):
    """Returns 'pong' if the bot is active"""
    await ctx.send("pong")

@bot.command()
async def join(ctx):
    """Join a voice channel"""
    user = ctx.message.author
    channel = user.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx):
    """Leave a voice channel"""
    await ctx.voice_client.disconnect()

@bot.command(pass_context=True)
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.User=None):
    """Simple kick command"""
    await ctx.guild.kick(member)
    kickMessage = "Successfully kicked" ,str(member)
    await ctx.channel.send("Successfully kicked" ,str(kickMessage))
    print("Successfully kicked" + " " + str(member))

@bot.command(pass_context=True)
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.User=None):
    """Simple ban command"""
    await ctx.guild.ban(member)
    banMessage = "Successfully banned" ,str(member)
    await ctx.channel.send(banMessage)
    print("Successfully banned" + " " + str(member))

bot.run(TOKEN)