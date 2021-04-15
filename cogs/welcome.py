import discord, os, asyncio, sqlite3, time
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.serverJSON import loadServerJson, updateServerJson

class Welcome(commands.Cog, name="welcome"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self,member):

        servers = loadServerJson()
        server = servers[str(member.guild.id)]
        welcome = server["welcome"]

        if welcome["enabled"] == 1:
            welcomeChannel = self.bot.get_channel(int(welcome["channel"]))
            welcomeMessage = welcome["message"].replace("{member}",member.mention).replace("{servername}",member.guild.name)
            await welcomeChannel.send(welcomeMessage)

def setup(bot):
    bot.add_cog(Welcome(bot))