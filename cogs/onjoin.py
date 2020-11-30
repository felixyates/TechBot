import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class Join(commands.Cog, name="join"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self,member):
        ment = member.mention
        server = member.guild.name
        async for guild in self.bot.fetch_guilds():
            if guild.id == 760406655472369705: # my 'gaming' server
                channel = self.bot.get_channel(760515090217828382) # welcome channel
                if server == 'gaming uno':
                    await channel.send("Welcome to "f"{server}, "f"{ment}!")

            elif guild.id == 772057284650074162: # george's 'gaming' server
                channel = self.bot.get_channel(777216612046209045) # welcome channel
                rulesChnl = self.bot.get_channel(777216612573904898)
                rulesChnl = rulesChnl.mention
                if server == 'gaming':
                    await channel.send("Welcome to "f"{server}, "f"{ment}! Head over to "f"{rulesChnl} to get started.")

            elif guild.id == 340043063798005780: # techlife server
                channel = self.bot.get_channel(777630965832089601) # welcome channel
                rulesChnl = self.bot.get_channel(537330037079277569)
                rulesChnl = rulesChnl.mention
                if server == 'TechLife':
                    await channel.send("Welcome to "f"{server}, "f"{ment}! Head over to "f"{rulesChnl} to get started.")

def setup(bot):
    bot.add_cog(Join(bot))