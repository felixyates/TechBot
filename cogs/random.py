import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self,ctx):
        "Says 'world'"
        await ctx.send("world")

    @commands.command()
    async def add(self,ctx, left : int, right : int):
        "Adds two numbers together."
        await ctx.send(left + right)

    @commands.command()
    async def servers(self,ctx):
        "Lists some cool beans servers you should join"
        await ctx.send("- gaming (#1): https://discord.gg/wWdr9bf\n- gaming (#2): https://discord.gg/bZFFgXnAVZ")

    @commands.command()
    async def ping(self,ctx):
        "Returns 'pong' if the bot is active"
        await ctx.send("pong")

def setup(bot):
    bot.add_cog(Random(bot))