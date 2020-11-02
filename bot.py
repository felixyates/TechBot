import discord
from discord.ext import commands

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
    """Says world"""
    await ctx.send("world")


@bot.command()
async def add(ctx, left : int, right : int):
    """Adds two numbers together."""
    await ctx.send(left + right)
    
@bot.event
async def on_message(message):
    if message.content == "shiver me timbers":
        await message.channel.send("https://tenor.com/view/slavicdaddy-slavic-oh-no-scared-shiver-me-timbers-gif-17482136")

@bot.event
async def on_message(message):
    if message.content == "shark pog":
        await message.channel.send("https://tenor.com/view/shark-pog-gif-18408265")
        


bot.run(TOKEN)
