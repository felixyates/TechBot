import discord, os, asyncio
from discord.ext import commands, tasks
from discord.ext.tasks import loop
from asyncio import sleep
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import tada_animated, dnd, online, yep, nope
from modules.serverJSON import loadServerJson

global maintenanceStatus, onlineVar, statusChannel
onlineVar = setembedvar("G",f"{online} Online",f"TechBot is back online and reporting for duty!",False)
statusChannel = 788802645070053377 # techbot, status
maintenanceStatus = 0

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

@loop(minutes=1)
async def status_update(self):
    if maintenanceStatus == 0:
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for >help"))
        await sleep(60)
        guildCount = await get_status_info(self,0)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{guildCount} servers"))
        await sleep(60)
        memberCount = await get_status_info(self,1)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{memberCount} members"))
        await sleep(60)

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

        print(f'Successfully logged in as {self.bot.user.name} / {self.bot.user.id}')
        print('------')

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

        serverEmbed = setembedvar("G","Servers")
        servers = loadServerJson()

        async for guild in self.bot.fetch_guilds():
            guild = self.bot.get_guild(guild.id)
            server = servers[str(guild.id)]
            serverMsg = f"""ID: `{guild.id}`
            Prefix: `{server["prefix"]}`
            Welcome: `{server["welcome"]["enabled"]}`, `{server["welcome"]["channel"]}`, `{server["welcome"]["message"]}`
            Slur Detector : `{server["slurdetector"]["enabled"]}`, `{server["slurdetector"]["channel"]}`
            Music: `{server["music"]["enabled"]}`, `{server["music"]["channel"]}`"""
            serverEmbed.add_field(name=guild.name,value=serverMsg)
            server = servers[str(guild.id)]

        await ctx.send(embed = serverEmbed)
    
    @commands.command()
    @commands.is_owner()
    async def leaveserver(self, ctx, id: int):

        to_leave = self.bot.get_guild(id)
        await to_leave.leave()
        
            

def setup(bot):
    bot.add_cog(Owner(bot))