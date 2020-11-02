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
async def shivermetimbers(message):
    if message.content == "shiver me timbers":
        await message.channel.send("https://tenor.com/view/slavicdaddy-slavic-oh-no-scared-shiver-me-timbers-gif-17482136")

@bot.event
async def sharkpog(message):
    if message.content == "shark pog":
        await message.channel.send("https://tenor.com/view/shark-pog-gif-18408265")

@bot.event
async def businessnoah(message):
    if message.content == "business noah":
        await message.channel.send("https://imgur.com/1qWWHKX")

@bot.event
async def george(message):
    if message.content == "george":
        await message.channel.send("https://imgur.com/yaQjd5t")

@bot.event
async def tom(message):
    if message.content == "tom":
        await message.channel.send("https://imgur.com/hL0kCQb")

@bot.event
async def thom(message):
    if message.content == "thom":
        await message.channel.send("https://imgur.com/bjYe6xZ")

@bot.event
async def felix(message):
    if message.content == "felix":
        await message.channel.send("https://imgur.com/SmSSQbA")
        
@bot.event
async def redditor(message):
    if message.content == "redditor":
        await message.channel.send("https://imgur.com/a2xKv7v")

@bot.event
async def harry(message):
    if message.content == "felix":
        await message.channel.send("https://imgur.com/0Ys8yM9")

@bot.event
async def fubz(message):
    if message.content == "felix":
        await message.channel.send("https://imgur.com/MpoS9PK")

@bot.event
async def marl(message):
    if message.content == "marl":
        await message.channel.send("https://imgur.com/Rxx5W5V")

@bot.event
async def smile(message):
    if message.content == "smile":
        await message.channel.send("https://imgur.com/8Ylxd5S")

@bot.event
async def foley(message):
    if message.content == "foley":
        await message.channel.send("https://imgur.com/Pn2X2xQ")

@bot.event
async def black(message):
    if message.content == "black":
        await message.channel.send("https://imgur.com/hbpWBDS")

@bot.event
async def wall(message):
    if message.content == "wall":
        await message.channel.send("https://imgur.com/zVnGKy6")

@bot.event
async def banwell(message):
    if message.content == "banwell":
        await message.channel.send("https://tenor.com/view/wow-omg-shocked-terrified-scared-gif-15766648")

@bot.event
async def dead(message):
    if message.content == "dead":
        await message.channel.send("https://tenor.com/view/dead-by-dayligh-t-mori-dance-dancing-pallbearer-coffin-dance-gif-17514251")

@bot.event
async def bunch(message):
    if message.content == "bunch":
        await message.channel.send("https://imgur.com/elbNWq9")

@bot.event
async def whale(message):
    if message.content == "whale":
        await message.channel.send("https://imgur.com/vLf8HAV")

@bot.event
async def gay(message):
    if message.content == "gay":
        await message.channel.send("https://cdn.discordapp.com/attachments/554724520725053450/771015120943448074/IMG_20201026_142316_454.jpg")

bot.run(TOKEN)
