import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

modCmds = []
modCmdsFile = open("cogs/moderation.txt")
modCmds = modCmdsFile.readlines()
modCmdsFile.close()

otherCmds = []
otherCmdsFile = open("cogs/other.txt")
otherCmds = otherCmdsFile.readlines()
otherCmdsFile.close()

ownerCmds = []
ownerCmdsFile = open("cogs/owner.txt")
ownerCmds = ownerCmdsFile.readlines()
ownerCmdsFile.close()

txtCmds = []
txtCmdsFile = open("cogs/textresponder.txt")
txtCmds = txtCmdsFile.readlines()
txtCmdsFile.close()

voiceCmds = []
voiceCmdsFile = open("cogs/voice.txt")
voiceCmds = voiceCmdsFile.readlines()
voiceCmdsFile.close()

availableEmbed = []
availableEmbedFile = open("voice/availableEmbed.txt")
availableEmbed = availableEmbedFile.readlines()
availableEmbedFile.close()

modules = ['Moderation','Text Responder','Voice','Available sound files to play','Other','Owner']

def converttostr(input_seq, separator):
   # Join all the strings in list
   final_str = separator.join(input_seq)
   return final_str

global helpVar
helpVar = discord.Embed(color=0x00ff00,title="Commands",description="Prefix"+ "- >")
helpVar.set_footer(text="Coded by TechLife.")
i = 0
for i in range(len(modules)):
    if modules[i] == 'Moderation':
        currentModule = ''.join(modCmds)
    elif modules[i] == 'Other':
        currentModule = ''.join(otherCmds)
    elif modules[i] == 'Owner':
        currentModule = ''.join(ownerCmds)
    elif modules[i] == 'Text Responder':
        currentModule = ''.join(txtCmds)
    elif modules[i] == 'Voice':
        currentModule = ''.join(voiceCmds)
    elif modules[i] == 'Available sound files to play':
        currentModule = ''.join(availableEmbed)
    helpVar.add_field(name=modules[i],value=currentModule, inline=False)
    i += 1

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
        serversVar = discord.Embed(color=0x00ff00,title="Servers",description="Here are some pretty cool beans servers you should join")
        serversVar.add_field(name="Gaming Servers",value="[The Dead One](https://discord.gg/wWdr9bf)\n[The Active One](https://discord.gg/mgwgcubfnk)")
        serversVar.add_field(name="The Dev's Server",value="[TechLife](https://discord.gg/uzyeYFN)", inline=False)
        await ctx.message.channel.send(embed=serversVar)

    @commands.command()
    async def ping(self,ctx):
        "Returns 'pong' if the bot is active"
        pingVar = discord.Embed(color=0xff0000,title="🏓 Pong!",description=f"Your ping is **{round(self.bot.latency *1000)}** ms!")
        await ctx.send(embed=pingVar)

    @commands.command()
    async def help(self,ctx):
        await ctx.message.channel.send(embed=helpVar)

def setup(bot):
    bot.add_cog(Other(bot))