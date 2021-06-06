import discord, os, asyncio, datetime
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import yep,nope

class Moderation(commands.Cog, name="moderation"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.User, *, reason = ""):
        "Simple kick command"

        #await ctx.guild.kick(member, reason=f"Kicked by {ctx.author.name} // {ctx.author.id}: {reason}")

        embed = discord.Embed(color = 0x00ff00, title = f"Kicked {member.name}", description = f"Successfully kicked {member.mention}.", timestamp = datetime.datetime.now())

        if reason == "":
            embed.add_field(name = "Reason", value = "No reason given.")
        else:
            embed.add_field(name = "Reason", value = reason)

        embed.set_footer(text = f"Kicked by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

        await ctx.channel.send(embed = embed)

    @commands.command()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, *, reason= ""):
        "Simple ban command"

        embed = discord.Embed(color = 0x00ff00, title = f"Banned {member.name}", description = f"Successfully banned {member.mention}.", timestamp = datetime.datetime.now())

        if reason != "":
            print(reason)
            reason = ctx.message.content.strip(member.mention)
            embed.add_field(name = "Reason", value = reason)
        else:
            embed.add_field(name = "Reason", value = "No reason given.")

        embed.set_footer(text = f"Banned by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

        #await ctx.guild.ban(member, reason=f"Banned by {ctx.author.name} // {ctx.author.id}: {reason}")

        await ctx.channel.send(embed = embed)
 
    @commands.command()
    @has_permissions(manage_messages=True)
    async def delete(self, ctx, deleteNumber: int):
        "Deletes a specied number of messages (max 100). Only works for messages under 14 days old, and you must have the 'Manage Messages' permission."
        if (deleteNumber >= 1) and (deleteNumber <=100):
            async with ctx.channel.typing():
                daysago = datetime.datetime.now() - datetime.timedelta(days=14)
                messages = await ctx.channel.history(limit=deleteNumber, after=daysago).flatten()
                await ctx.channel.delete_messages(messages)
                await ctx.message.delete()
                embedVar = setembedvar("G","Deleted messages",f"{yep} Deleted {len(messages)} messages.",False)
                await ctx.message.channel.send(embed=embedVar,delete_after=5)
        else:
            embedVar = setembedvar("R","Didn't delete messages",f"{nope} The number of deleted messages must be between 1 and 100, not {deleteNumber}!",False)
            await ctx.message.channel.send(embed=embedVar,delete_after=5)

    @commands.command()
    @has_permissions(manage_messages=True)
    async def purge(self, ctx):
        daysago = datetime.datetime.now() - datetime.timedelta(days=14)
        "Deletes 100 messages under 14 days old."
        async with ctx.channel.typing():
            messages = await ctx.channel.history(limit=100, after=daysago).flatten()
            await ctx.channel.delete_messages(messages)
            embedVar = setembedvar("G","Deleted messages",f"{yep} Deleted {len(messages)} messages.",False)
            await ctx.message.channel.send(embed=embedVar,delete_after=5)

def setup(bot):
    bot.add_cog(Moderation(bot))