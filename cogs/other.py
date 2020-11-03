import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class Other(commands.Cog, name="other"):
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

    @commands.command()
    async def help(self,ctx):
        embedVar = discord.Embed(color=0x00ff00)
        embedVar.add_field(name="Moderation",value=commands, inline=False)
        embedVar.add_field(name="Text Responder",value="shiver me timbers\nshark pog\nbusiness noah\ngeorge\ntom\nthom\nfelix\nredditor\nharry\nfubz\nmarl\nsmile\nfoley\nblack\nwall\nbanwell\ndead\nbunch\nwhale\ngay")
        embedVar.add_field(name="Voice",value="fnaf - Plays the FNAF phone call in the voice channel\ncats - As per Harry's request. Don't even ask.\nstop - Stops the currently playing audio in voice chat.", inline=False)
        embedVar.add_field(name="Other",value="hello - Says 'world'.\nadd - Adds two numbers together.\nservers - Lists some cool beans servers you should join.\nping - Returns 'pong' is the bot is online.\nhelp - Shows this message.", inline=False)
        embedVar.add_field(name="Owner",value="Note, this commands can only be used by the bot's owner.\nshutdown - Shuts the bot down.\nload <extension> - Loads the specified extension.\nunload <extension> - Unloads the specified extension.", inline=False)
        await ctx.message.channel.send(embed=embedVar)

def setup(bot):
    bot.add_cog(Other(bot))