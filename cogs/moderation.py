import discord, datetime, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from modules.emoji import yep,nope
from discord_slash import cog_ext

# Command functions

async def kick(self, ctx, member: discord.User, *, reason = ""):

    await ctx.guild.kick(member, reason=f"Kicked by {ctx.author.name} // {ctx.author.id}: {reason}")
    
    embed = discord.Embed(color = 0x00ff00, title = f"Kicked {member.name}", description = f"Successfully kicked {member.mention}.", timestamp = datetime.datetime.now())

    if reason == "":
        embed.add_field(name = "Reason", value = "No reason given.")
    else:
        embed.add_field(name = "Reason", value = reason)

    embed.set_footer(text = f"Kicked by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

    await ctx.send(embed = embed)

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
    await ctx.channel.send(embed = embed)

async def delete(self, ctx, deletenumber: int):
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

async def purge(self, ctx):
    await ctx.send("Working on it...")
    daysago = datetime.datetime.now() - datetime.timedelta(days=14)
    async with ctx.channel.typing():
        messages = await ctx.channel.history(limit=100, after=daysago).flatten()
        await ctx.channel.delete_messages(messages)
        await ctx.send(f"{yep} Deleted {len(messages)} messages.")

async def slowdelete(self, ctx, messages: int):
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

# Slash command choices and options

kick_options = [{"name":"user","description":"User to kick","type":6,"required":"true"},{"name":"reason","description":"Reason for kicking user","type":3,"required":"false"}]
ban_options = [{"name":"user","description":"User to ban","type":6,"required":"true"}]
delete_options = [{"name":"messages","description":"Number of messages to delete","type":4,"required":"true"}]
slowdelete_options = [{"name":"messages","description":"Number of messages to delete","type":4,"required":"true"}]

class Moderation(commands.Cog, name="moderation"):

    def __init__(self, bot):
        self.bot = bot

    # Kick

    @cog_ext.cog_slash(name="kick", description="Simple kick command")
    @has_permissions(kick_members=True)
    async def slash_kick(self, ctx, member, reason):
        await kick(self, ctx, member, reason)

    @commands.command(name="kick")
    @has_permissions(kick_members=True)
    async def regular_kick(self, ctx, member: discord.User, *, reason = ""):
        await kick(self, ctx, member, reason)

    # Ban

    @cog_ext.cog_slash(name="ban", description="Simple ban command", options=ban_options)
    @has_permissions(ban_members=True)
    async def slash_ban(self, ctx, member, reason):
        await ban(self, ctx, member, reason)

    @commands.command(name="ban")
    @has_permissions(ban_members=True)
    async def regular_ban(self, ctx, member: discord.User, *, reason= ""):
        await ban(self, ctx, member, reason)

    # Delete

    @cog_ext.cog_slash(name="delete", description="Deletes a specified number of messages (max 100, up to 14 days old)", options=delete_options)
    @has_permissions(manage_messages=True)
    async def slash_delete(self, ctx, deletenumber):
        await delete(self, ctx, deletenumber)

    @commands.command(name="delete")
    @has_permissions(manage_messages=True)
    async def regular_delete(self, ctx, deletenumber: int):
        await delete(self, ctx, deletenumber)

    # Purge

    @cog_ext.cog_slash(name="purge", description="Deletes 100 messages under 14 days old.")
    @has_permissions(manage_messages=True)
    async def slash_purge(self, ctx):
        await purge(self, ctx)

    @commands.command(name="purge")
    @has_permissions(manage_messages=True)
    async def regular_purge(self, ctx):
        await purge(self, ctx)

    # Slow delete

    @cog_ext.cog_slash(name="slowdelete", description="Deletes specified number of messages (up to 1000). Not restricted by age of message.", options=slowdelete_options)
    @has_permissions(manage_messages=True)
    async def slash_slowdelete(self, ctx, messages):
        await slowdelete(self, ctx, messages)
    
    @commands.command(name="slowdelete")
    @has_permissions(manage_messages=True)
    async def regular_slowdelete(self, ctx, messages: int):
        await slowdelete(self, ctx, messages)

def setup(bot):
    bot.add_cog(Moderation(bot))