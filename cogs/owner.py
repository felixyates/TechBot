import discord, os, asyncio
from discord.ext import commands, tasks
from discord.ext.tasks import loop
from asyncio import sleep
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import tada_animated, dnd, online, offline, yep, nope, loading, wave_animated
from modules.serverJSON import loadServerJson

global maintenanceStatus, onlineVar, statusChannel
onlineVar = setembedvar("G",f"{online} Online",f"TechBot is back online and reporting for duty!",False)
statusChannel = 788802645070053377 # techbot, status
maintenanceStatus = 0

@loop(seconds=60)
async def status_update(self):

    delay = 60 # seconds


    if maintenanceStatus == 0:
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for >help"))
        await sleep(delay)
    

    if maintenanceStatus == 0:
        guildCount = await get_status_info(self,0)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{guildCount} servers"))
        await sleep(delay)
    

    if maintenanceStatus == 0:
        memberCount = await get_status_info(self,1)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{memberCount} members"))
        await sleep(delay)

async def setstatus(self, ctx, status, type):

    global maintenanceStatus

    if status != "":
            
        oldstatus = status
        spaces = ctx.message.content.split(" ")
        if len(spaces) > 2:
            status = ctx.message.content.split(status)
            newStatus = f"{oldstatus}{status[1]}"
        else:
            newStatus = status

        try:

            if type == "playing":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=newStatus))

            elif type == "listening":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=newStatus))

            elif type == "watching":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=newStatus))
        
            elif type == "streaming":
                await self.bot.change_presence(activity=discord.Streaming(url="https://www.twitch.tv/techlifeyt",name=newStatus))

            maintenanceStatus = 1

            success = setembedvar("G","Success!", description = f"Changed status to `{newStatus}`.")

            status_update.cancel()
            await ctx.send(embed = success)

        except Exception as e:

            failure = setembedvar("R","Uh oh!", description = f"Couldn't update status; `{e}`")
            await ctx.send(embed = failure)

    else:
            
        maintenanceStatus = 0

        if status_update.is_running() == True:

            status_update.restart(self)
            description = f"{yep} Restarted status cycle."
        
        else:

            status_update.start(self)
            description = f"{yep} Started status cycle."
        
        await ctx.send(embed = setembedvar("G","Reset Status", description = description))

        

async def get_status_info(self,mode):

    guildCount = memberCount = 0

    async for guild in self.bot.fetch_guilds():
        guild = self.bot.get_guild(guild.id)
        guildCount += 1
        memberCount += guild.member_count

    if mode == 0: # guildCount
        return guildCount
    elif mode == 1: # memberCount
        return memberCount

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self,ctx):
        await ctx.message.add_reaction('✅')
        await self.bot.close()
        quit()
    
    @commands.Cog.listener()
    async def on_ready(self):

        print(f"Successfully logged in as {self.bot.user.name} / {self.bot.user.id}"+"\n------")

        status_update.start(self)

        channel = self.bot.get_channel(statusChannel)
        await channel.send(embed = onlineVar)

    
    @commands.command()
    @commands.is_owner()
    async def maintenance(self, ctx, status: str):
        global maintenanceStatus
        if status == "on":

            maintenanceStatus = 1

            channel = self.bot.get_channel(statusChannel)

            maintenanceVar = setembedvar("R",f"{dnd} Maintenance",f"TechBot is currently undergoing maintenance."+"\nThis means that most, if not all, commands will be unavailable.\nCheck back here for updates.")
            await channel.send(embed = maintenanceVar)
            await ctx.channel.send(embed = setembedvar("G",f"Success",f"{yep} Maintenance mode enabled"))
            await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name="for updates. The bot is currently undergoing maintenance and so some (if not all) commands will be unavailable."))

            status_update.cancel()

        elif status == "off":

            maintenanceStatus = 0
            status_update.start(self)

            channel = self.bot.get_channel(statusChannel)
            await channel.send(embed = onlineVar)

        else:
            await ctx.channel.send(embed = setembedvar("R","Incorrect command usage.",f"{nope} Enter 'on' or 'off'."))
        
    @commands.command()
    @commands.is_owner()
    async def botservers(self, ctx):

        description = f"{loading} Hold on, this could take a while!"+"\nDiscord will be ratelimiting these messages..."

        await ctx.send(embed = setembedvar("G","Getting all servers...", description = description))
        servers = loadServerJson()

        async for guild in self.bot.fetch_guilds():
            guild = self.bot.get_guild(guild.id)
            server = servers[str(guild.id)]
            serverEmbed = setembedvar("G", guild.name, thumbnail = guild.icon_url)
            serverEmbed.add_field(name="Prefix", value= f"`{server['prefix']}`")
            serverEmbed.add_field(name="Guild ID", value= f"`{guild.id}`")
            serverEmbed.add_field(name="Slur Detector", value= f'`{server["slurdetector"]["enabled"]}`, `{server["slurdetector"]["channel"]}`')
            serverEmbed.add_field(name="Music", value= f'`{server["music"]["enabled"]}`, `{server["music"]["channel"]}`')
            serverEmbed.add_field(name="Welcome", value= f'`{server["welcome"]["enabled"]}`, `{server["welcome"]["channel"]}`'+"\n"+f'`{server["welcome"]["message"]}`')
            await ctx.send(embed = serverEmbed)
    
    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx, id: int):

        to_leave = self.bot.get_guild(id)
        await to_leave.leave()

    @commands.command()
    @commands.is_owner()
    async def playing(self, ctx, status = ""):

        await setstatus(self, ctx, status, "playing")

    @commands.command()
    @commands.is_owner()
    async def listening(self, ctx, status = ""):

        await setstatus(self, ctx, status, "listening")

    @commands.command()
    @commands.is_owner()
    async def streaming(self, ctx, status = ""):

        await setstatus(self, ctx, status, "streaming")

    @commands.command()
    @commands.is_owner()
    async def watching(self, ctx, status = ""):

        await setstatus(self, ctx, status, "watching")

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send(embed = setembedvar("G", "Logging out", f"{wave_animated} See you soon!"))
        channel = self.bot.get_channel(statusChannel)
        await channel.send(embed = setembedvar(0x747F8E, f"{offline} Offline", f"The bot is going offline. Check here for updates."))
        await self.bot.logout()
            

def setup(bot):
    bot.add_cog(Owner(bot))