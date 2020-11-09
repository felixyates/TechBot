import discord
import os
import asyncio
#import youtube_dl
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
        with document(title='TechBot Status') as doc:
            p('TechBot is offline')
        with open('/var/www/html/index.html', 'w') as f:
            f.write(doc.render())
            quit()

def setup(bot):
    bot.add_cog(Owner(bot))