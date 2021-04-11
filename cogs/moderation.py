import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import yep,nope

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
        msgList = msg.split(" ")
        deleteNo = int(msgList[1])
        if (deleteNo >= 0) and (deleteNo <=100):
            async with channel.typing():
                messages = await channel.history(limit=deleteNo+1).flatten()
                await ctx.channel.delete_messages(messages)
                embedVar = setembedvar("G","Deleted messages",f"{yep} Deleted {deleteNo} messages.",False)
                await ctx.message.channel.send(embed=embedVar,delete_after=5)
        else:
            embedVar = setembedvar("R","Didn't delete messages",f"{nope} The number of deleted messages must be between 0 and 100, not {deleteNo}!",False)
            await ctx.message.channel.send(embed=embedVar,delete_after=5)

def setup(bot):
    bot.add_cog(Moderation(bot))