import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self,ctx):
        await ctx.message.add_reaction('✅')
        await self.bot.close()
        quit()
    
    @commands.command()
    @commands.is_owner()
    async def maintenance(self, status: str):
        if status == "enabled":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="for updates. The bot is currently undergoing maintenance and so some (if not all) commands will be unavailable."))
        elif status == "disabled":
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for >help"))

def setup(bot):
    bot.add_cog(Owner(bot))