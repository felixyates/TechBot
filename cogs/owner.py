import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from dominate import document
from dominate.tags import *

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self,ctx):
        await ctx.message.add_reaction('✅')
        await self.bot.close()
        quit()

def setup(bot):
    bot.add_cog(Owner(bot))