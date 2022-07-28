import discord
from discord.ext import commands
import discord.ext.tasks as tasks
from async_timeout import timeout
from modules import embs, emoji, db

cases = [] # [case number,user id]
warnings = [] # [user id,number of warnings]

@tasks.loop(seconds = 60)
async def status_update(self):
    global servers
    servers = await db.loadServers()

async def updateServerCache(guildID):
    "Refreshes individual server in cache after it is updated."
    global servers
    servers[str(guildID)] = Server(str(guildID)).GetJson()

with open("cogs/blocklist.txt","r") as slurfile:
    loaded = slurfile.readlines()
    blockedwords = []
    for line in loaded:
        blockedwords.append(line.strip("\n").split(","))

class User():

    def __init__(self, user: discord.User):
        self.name = user.display_name
        self.id = user.id

class Server():

    def __init__(self, server: discord.Guild):
        self.name = server.name
        self.id = server.id
        self.modChannel = Server(self.id).GetModule().channel
    
    async def CreateCaseFile():
        print()

class Case():

    def __init__(self, message: discord.Message, detected, server):
        self.author = User(message.author)
        self.server = Server(server)
        self.message = message.content
        self.channel = message.channel.id
        self.detected = detected

    async def Open():
        print()

    async def Close():
        print()

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
                servers[gldID] = Server(gldID).GetJSON() # add server to cache
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