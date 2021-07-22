import discord, datetime, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from modules.embedvars import setembedvar
from modules.emoji import yep,nope
from discord_slash import cog_ext
from bot import commandWarning


class Moderation(commands.Cog, name="moderation"):



    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.User, *, reason = ""):
        "Simple kick command"

        await ctx.guild.kick(member, reason=f"Kicked by {ctx.author.name} // {ctx.author.id}: {reason}")

        embed = discord.Embed(color = 0x00ff00, title = f"Kicked {member.name}", description = f"Successfully kicked {member.mention}.", timestamp = datetime.datetime.now())

        if reason == "":
            embed.add_field(name = "Reason", value = "No reason given.")
        else:
            embed.add_field(name = "Reason", value = reason)

        embed.set_footer(text = f"Kicked by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

        await ctx.reply(embed = embed, mention_author=False)
        await commandWarning(ctx)



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

        await ctx.guild.ban(member, reason=f"Banned by {ctx.author.name} // {ctx.author.id}: {reason}")
        await ctx.reply(embed = embed, mention_author=False)
        await commandWarning(ctx)
 


    @commands.command()
    @has_permissions(manage_messages=True)
    async def delete(self, ctx, deleteNumber: int):
        "Deletes a specied number of messages (max 100). Only works for messages under 14 days old, and you must have the 'Manage Messages' permission."
        if (deleteNumber >= 1) and (deleteNumber <=100):
            async with ctx.channel.typing():
                daysago = datetime.datetime.now() - datetime.timedelta(days=14)
                await ctx.message.delete()
                messages = await ctx.channel.history(limit=deleteNumber, after=daysago).flatten()
                if len(messages) > 0:
                    await ctx.channel.delete_messages(messages)
                    embedVar = setembedvar("G","Deleted messages",f"{yep} Deleted {len(messages)} messages.")
                    await ctx.message.channel.send(embed=embedVar,delete_after=5)
                else:
                    embedVar = setembedvar("R","Couldn't delete messages",f"{nope} Messages either not found or sent more than 14 days ago.")
                    await ctx.message.channel.send(embed=embedVar,delete_after=10)
        else:
            embedVar = setembedvar("R","Didn't delete messages",f"{nope} The number of deleted messages must be between 1 and 100, not {deleteNumber}!",False)
            await ctx.message.channel.send(embed=embedVar,delete_after=5)
        await commandWarning(ctx)


    @commands.command()
    @has_permissions(manage_messages=True)
    async def purge(self, ctx):
        "Deletes 100 messages under 14 days old."
        daysago = datetime.datetime.now() - datetime.timedelta(days=14)
        async with ctx.channel.typing():
            messages = await ctx.channel.history(limit=100, after=daysago).flatten()
            await ctx.channel.delete_messages(messages)
            embedVar = setembedvar("G","Deleted messages",f"{yep} Deleted {len(messages)} messages.",False)
            await ctx.message.channel.send(embed=embedVar,delete_after=5)
        await commandWarning(ctx)


    @commands.command()
    @has_permissions(manage_messages=True)
    async def slowdelete(self, ctx, deleteNumber: int):
        "Deletes specified number of messages (up to 1000). Not restricted by age of message."
        confirmationMessage = await ctx.send(f"Attempting to delete {deleteNumber} messages. This will take a long time, depending on how messages you want to delete, and cannot be cancelled or undone. Are you sure you want to do this?")
        await confirmationMessage.add_reaction(yep)
        await confirmationMessage.add_reaction(nope)
        async with ctx.channel.typing():
            ""
        await commandWarning(ctx)


    kick_options = [{"name":"user","description":"User to kick","type":6,"required":"true"},{"name":"reason","description":"Reason for kicking user","type":3,"required":"false"}]
    @cog_ext.cog_slash(name="kick", description="Simple kick command")
    @has_permissions(kick_members=True)
    async def slash_kick(self, ctx, member: discord.User, *, reason = ""):

        await ctx.guild.kick(member, reason=f"Kicked by {ctx.author.name} // {ctx.author.id}: {reason}")

        working = await ctx.send("Working on it...")
        embed = discord.Embed(color = 0x00ff00, title = f"Kicked {member.name}", description = f"Successfully kicked {member.mention}.", timestamp = datetime.datetime.now())

        if reason == "":
            embed.add_field(name = "Reason", value = "No reason given.")
        else:
            embed.add_field(name = "Reason", value = reason)

        embed.set_footer(text = f"Kicked by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

        await ctx.channel.send(embed = embed)
        await working.delete()



    ban_options = [{"name":"user","description":"User to ban","type":6,"required":"true"}]
    @cog_ext.cog_slash(name="ban", description="Simple ban command", options=ban_options)
    @has_permissions(ban_members=True)
    async def slash_ban(self, ctx, member: discord.User, *, reason= ""):
        "Simple ban command"

        embed = discord.Embed(color = 0x00ff00, title = f"Banned {member.name}", description = f"Successfully banned {member.mention}.", timestamp = datetime.datetime.now())

        if reason != "":
            print(reason)
            reason = ctx.message.content.strip(member.mention)
            embed.add_field(name = "Reason", value = reason)
        else:
            embed.add_field(name = "Reason", value = "No reason given.")

        embed.set_footer(text = f"Banned by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

        await ctx.guild.ban(member, reason=f"Banned by {ctx.author.name} // {ctx.author.id}: {reason}")
        await ctx.channel.send(embed = embed)



    delete_options = [{"name":"messages","description":"Number of messages to delete","type":4,"required":"true"}]
    @cog_ext.cog_slash(name="delete", description="Deletes a specified number of messages (max 100, up to 14 days old)", options=delete_options)
    @has_permissions(manage_messages=True)
    async def slash_delete(self, ctx, deletenumber: int):
        if (deletenumber >= 1) and (deletenumber <=100):
            await ctx.send("Working on it...")
            async with ctx.channel.typing():
                daysago = datetime.datetime.now() - datetime.timedelta(days=14)
                await ctx.message.delete()
                messages = await ctx.channel.history(limit=deletenumber, after=daysago).flatten()
                if len(messages) > 0:
                    await ctx.channel.delete_messages(messages)
                    await ctx.send(f"{yep} Deleted {len(messages)} messages.")
                else:
                    await ctx.send(f"{nope} Messages either not found or sent more than 14 days ago.")
        else:
            await ctx.send(f"{nope} The number of deleted messages must be between 1 and 100, not {deletenumber}!")



    @cog_ext.cog_slash(name="purge", description="Deletes 100 messages under 14 days old.")
    @has_permissions(manage_messages=True)
    async def slash_purge(self, ctx):
        await ctx.send("Working on it...")
        daysago = datetime.datetime.now() - datetime.timedelta(days=14)
        async with ctx.channel.typing():
            messages = await ctx.channel.history(limit=100, after=daysago).flatten()
            await ctx.channel.delete_messages(messages)
            await ctx.send(f"{yep} Deleted {len(messages)} messages.")



    slowdelete_options = [{"name":"messages","description":"Number of messages to delete","type":4,"required":"true"}]
    @cog_ext.cog_slash(name="slowdelete", description="Deletes specified number of messages (up to 1000). Not restricted by age of message.", options=slowdelete_options)
    @has_permissions(manage_messages=True)
    async def slash_slowdelete(self, ctx, messages: int):
        try:
            i = 0
            async with ctx.channel.typing():
                messagesList = await ctx.channel.history(limit=messages).flatten()
                confirmationMessage = await ctx.send(f"Attempting to delete {messages} messages. This will take a long time, depending on how messages you want to delete. Are you sure you want to do this?")
                await confirmationMessage.add_reaction(yep)

                def check(reaction, user):
                    if reaction == yep and user == ctx.author:
                        return

                try:
                    await self.bot.wait_for('reaction_add', timeout=30, check=check)
                except asyncio.TimeoutError:
                    await ctx.send(f"{nope} Response timed out. Reinvoke the command if you want to continue.")

                for message in messagesList:
                    await message.delete()
                    i += 1
                    if i%10 == 0:
                        await confirmationMessage.edit(content=f"Progress: {(i/messages)*100}% deleted ({i}/{messages})")
                if i == messages:
                    await confirmationMessage.edit(content=f"{yep} Deleted {i} messages.", delete_after=5)
        except Exception as e:
            await ctx.send(f"{nope} Couldn't delete messages. Try again or contact support.")
            print(e)



def setup(bot):
    bot.add_cog(Moderation(bot))