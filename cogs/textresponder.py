import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

def converttostr(input_seq, separator):
   # Join all the strings in list
   final_str = separator.join(input_seq)
   return final_str

# Adds all text commands and urls to a file
global txtURLS
global txtCmds

temp = []
temp2 = []
txtURLS = []
txtCmds = []

with open('cogs/textresponderLinks.txt', 'r') as f:
                temp = f.read().splitlines()
                i = 0
                for i in range(len(temp)):
                    current = temp[i]
                    current2 = current.split(",")
                    i+=1
                    x = 0
                    for x in range(len(current2)):
                        temp2.append(current2[x])
                        x+=1

y = 0
for y in range(len(temp2)):
    if y % 2:
        txtURLS.append(temp2[y])
    else:
        txtCmds.append(temp2[y])   

class TextResponder(commands.Cog, name="textresponder"):
    def __init__(self,bot):
        self.bot = bot

# Checks sent messages. If the message is one of the commands in the file, it will send the specified URL.

    @commands.Cog.listener()
    async def on_message(self,message):
        z = 0
        for z in range(len(txtCmds)):
            if message.content == txtCmds[z]:
                await message.channel.send(txtURLS[z])
            z+=1
        if "nigg" in message.content:
            await message.channel.send("DO NOT SAY THAT!!! "+message.author.mention)
    
    @commands.command()
    @commands.is_owner()
    async def spam(self,ctx):
        q = 0
        for q in range(len(txtURLS)):
            await ctx.send(txtURLS[q])
            q+=1

def setup(bot):
    bot.add_cog(TextResponder(bot))