import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
import sqlite3

def converttostr(input_seq, separator):
   # Join all the strings in list
   final_str = separator.join(input_seq)
   return final_str

global helpVar
helpVar = discord.Embed(color=0x00ff00,title="Commands",description="Prefix"+ "- >")
helpVar.set_footer(text="Coded by TechLife.")

with sqlite3.connect('commands.db') as db:
    cursor = db.cursor()
    for i in range(1,7):
        rows = cursor.execute("SELECT * FROM commands WHERE id = ?",(i,))
        moduleCmds = []
        for row in rows:
            command = row[1]
            purpose = row[2]
            moduleCmds.append(f"{command}: {purpose}\n")
        for x in range(len(moduleCmds)):
            moduleCmds[x] = moduleCmds[x].replace('"',"").replace(",","\n")
        print(moduleCmds)
        displaynames = cursor.execute("SELECT displayname FROM modules WHERE id = ?",(i,))
        for row in displaynames:
            displayname = row[0]
        helpVar.add_field(name=displayname,value=''.join(moduleCmds), inline=False)
        
db.close()

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