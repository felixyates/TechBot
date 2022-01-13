import discord, asyncio, os, json
from discord.ext import commands
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import yep,nope,blob_ban
from modules.getjson import loadServerJson, thisServerJson, updateServerJson

cases = [] # [case number,user id]
warnings = [] # [user id,number of warnings]
servers = loadServerJson()

async def updateServerCache(guildID):
    "Refreshes individual server in cache after it is updated."
    global servers
    servers[str(guildID)] = thisServerJson(str(guildID))

with open("cogs/blocklist.txt","r") as slurfile:
    loaded = slurfile.readlines()
    blockedwords = []
    for line in loaded:
        blockedwords.append(line.strip("\n").split(","))

class Case(object):

    async def Create(message, server):
        author = message.author

class SlurDetector(commands.Cog, name="slurdetector"):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        gldID = str(message.guild.id)

        try:
            server = servers[gldID] # fetch server from cache
        except: # if server doesn't exist in cache
            try:
                servers[gldID] = thisServerJson(gldID) # add server to cache
                server = servers[gldID]  
            except: # server doesn't exist in servers file, uh oh
                return
        
        if server["slurdetector"]["enabled"] == 1:
            for word in blockedwords:
                if word[0] in message.content:
                    # CALL CASE HANDLER
                    ""

def setup(bot):
    bot.add_cog(SlurDetector(bot))