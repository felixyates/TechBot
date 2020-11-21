import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from dominate import document
from dominate.tags import *
import smtplib, ssl
from email.message import EmailMessage

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self,ctx):
        await ctx.message.add_reaction('✅')
        context = ssl.create_default_context()
        fromaddr = "techbot@techlifeyt.com"
        toaddr = "component+f21dd98f-ebf2-4ec1-bbbb-d0ca2863ddad@notifications.statuspage.io"
        msg = """\
Subject: DOWN

The shutdown command was used."""
        with smtplib.SMTP_SSL('techlifeyt.com', 465, context=context) as server:
            server.login("techbot@techlifeyt.com", "3RzbbdD74$BJ")
            server.sendmail(fromaddr, toaddr, msg)
        await self.bot.close()
        quit()

def setup(bot):
    bot.add_cog(Owner(bot))