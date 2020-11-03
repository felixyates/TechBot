import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class TextResponder(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.content == "shiver me timbers":
            await message.channel.send("https://tenor.com/view/slavicdaddy-slavic-oh-no-scared-shiver-me-timbers-gif-17482136")
        if message.content == "shark pog":
            await message.channel.send("https://tenor.com/view/shark-pog-gif-18408265")
        if message.content == "business noah":
            await message.channel.send("https://imgur.com/1qWWHKX")
        if message.content == "george":
            await message.channel.send("https://imgur.com/yaQjd5t")
        if message.content == "tom":
            await message.channel.send("https://imgur.com/hL0kCQb")
        if message.content == "thom":
            await message.channel.send("https://imgur.com/bjYe6xZ")
        if message.content == "felix":
            await message.channel.send("https://imgur.com/SmSSQbA")
        if message.content == "redditor":
            await message.channel.send("https://imgur.com/a2xKv7v")
        if message.content == "harry":
            await message.channel.send("https://imgur.com/0Ys8yM9")
        if message.content == "fubz":
            await message.channel.send("https://imgur.com/MpoS9PK")
        if message.content == "marl":
            await message.channel.send("https://imgur.com/Rxx5W5V")
        if message.content == "smile":
            await message.channel.send("https://imgur.com/8Ylxd5S")
        if message.content == "foley":
            await message.channel.send("https://imgur.com/Pn2X2xQ")
        if message.content == "black":
            await message.channel.send("https://imgur.com/hbpWBDS")
        if message.content == "wall":
            await message.channel.send("https://imgur.com/zVnGKy6")
        if message.content == "banwell":
            await message.channel.send("https://tenor.com/view/wow-omg-shocked-terrified-scared-gif-15766648")
        if message.content == "dead":
            await message.channel.send("https://tenor.com/view/dead-by-dayligh-t-mori-dance-dancing-pallbearer-coffin-dance-gif-17514251")
        if message.content == "bunch":
            await message.channel.send("https://imgur.com/elbNWq9")
        if message.content == "whale":
            await message.channel.send("https://imgur.com/vLf8HAV")
        if message.content == "gay":
            await message.channel.send("https://cdn.discordapp.com/attachments/554724520725053450/771015120943448074/IMG_20201026_142316_454.jpg")

def setup(bot):
    bot.add_cog(TextResponder(bot))