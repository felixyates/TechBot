import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class Moderation(commands.Cog, name="moderation"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @has_permissions(kick_members=True)
    async def kick(self,ctx, member: discord.User=None):
        "Simple kick command"
        await ctx.guild.kick(member)
        kickMessage = "Successfully kicked" ,str(member)
        await ctx.channel.send("Successfully kicked" ,str(kickMessage))
        print("Successfully kicked" + " " + str(member))

    @commands.command(pass_context=True)
    @has_permissions(ban_members=True)
    async def ban(self,ctx, member: discord.User=None):
        "Simple ban command"
        await ctx.guild.ban(member)
        banMessage = "Successfully banned" ,str(member)
        await ctx.channel.send(banMessage)
        print("Successfully banned" + " " + str(member))
 
    @commands.command(pass_context=True)
    @has_permissions(manage_messages=True)
    async def purge(self,ctx):
        "Deletes a specied number of messages (max 100).Only works for messages under 14 days old, and you must have the 'Manage Messages' permission. Currently broken, too."
        channel = ctx.channel
        msg = str(ctx.message.content)
        print(msg)
        msgList = msg.split( )
        print(msgList)
        deleteNo = int(msgList[1])
        print(deleteNo)
        async with channel.typing():
            await ctx.channel.delete_messages(deleteNo)
            await ctx.channel.send("Deleted "+ deleteNo +" messages.",delete_after="5")

def setup(bot):
    bot.add_cog(Moderation(bot))