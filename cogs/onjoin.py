import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.emoji import nope,yep,tada_animated
import sqlite3
import time
from modules.embedvars import setembedvar

global listening
listening = False

class ChannelDoesNotExist(Exception):
    pass

class Join(commands.Cog, name="join"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcomesetup(self,ctx):

        ## Allows for guild admins to create / set a custom welcome message for their server.
        ## Syntax: >welcomesetup
        ## Placeholders for message: {member} and {servername}

        global author
        author = ctx.author
        success1 = success2 = False

        timedOutVar = setembedvar("R","Setup Expired",f"{nope} Didn't receive response. Run `>welcomesetup` to restart setup.",False)

        cancelledMsg = """Cancelled welcome message setup.
                        You can always run >welcomesetup to start again."""
        cancelledVar = setembedvar("R","Cancelled Setup",cancelledMsg,False)

        embedOneMsg = """What's the ID of the channel you'd like the welcome message to be sent to?

        Hint: you can get this by enabling *Developer Mode* in Discord's advanced settings, then right-clicking on the channel and 'Copy ID'."""

        embedOne = setembedvar("G","Welcome Message Setup",embedOneMsg,False)
        embedOne.set_footer(text="Or, enter `cancel` to cancel.")
        await ctx.send(embed=embedOne)

        async def doesChannelExist(channelID):
            # Checks to see if channel exists in guild

            channelExists = False

            for guild in self.bot.guilds:
                if guild.id == ctx.guild.id:
                    for channel in guild.text_channels:
                        if channel.id == channelID:
                            channelExists = True
                            await ctx.send(embed=setembedvar("G","Channel exists",f"{yep} Welcome message channel set to <#{channelID}>.",False))
                            shouldContinue = True
                            success1 = True
                            return shouldContinue, success1, channelID

            if channelExists == False:
                raise ChannelDoesNotExist(f"Channel {channelID} not found.")


        def channelIDcheck(m):
            # Checks if message is:
                # a) from command issuer
                # b) requesting cancellation
                # c) an integer
            if authorCheck(m) == True:
                cancelled = cancelcheck(m)
                if cancelled == True:
                    print("Exited cancelcheck with True, cancelling setup.")
                    return "cancel"
                elif cancelled == False:
                    try:
                        return int(m.content)
                    except:
                        raise ValueError
            else:
                print("Message not from command issuer.")
        
        def welcomeMessageCheck(m):
            # Checks if message is:
                # a) from command issuer
                # b) requesting cancellation
            if authorCheck(m) == True:
                cancelled = cancelcheck(m)
                if cancelled == True:
                    print("Exited cancelcheck with True, cancelling setup.")
                    return "cancel"
                else:
                    return m.content
            else:
                print("Message not from command issuer.")

        def cancelcheck(m):
            # Checks if user desires to cancel setup.
            print(f"Entered cancelcheck with {m.content}")
            if m.content == "cancel":
                print("User cancelled setup.")
                return True
            else:
                print("User continuing with setup.")
                return False
        
        def authorCheck(m):
            # Checks if message is from command issuer.
            if m.author.id == author.id:
                return True
            else:
                return False

        async def welcomeChannel():
            # Prompts user to give channel ID.
            # Waits for response or until timeout.
            # Checks message and to see if channel exists.
            # Keeps waiting if user enters wrong format message or wrong channel ID.

            shouldContinue = hasTimedOut = cancelled = success1 = False
        
            while shouldContinue == False and hasTimedOut == False and cancelled == False:
                print("In welcome message channel loop.")
                try:
                    msg = await self.bot.wait_for('message', timeout=30.0, check=channelIDcheck)

                    if msg.content == "cancel":
                        cancelled = True
                        await ctx.send(embed=cancelledVar)
                    else:
                        shouldContinue, success1, welcomeChannel = await doesChannelExist(int(msg.content))

                except asyncio.TimeoutError:
                    hasTimedOut = True
                    print("Setup timed out")
                    await ctx.send(embed=timedOutVar)
        
                except ValueError:
                    await ctx.send(embed=setembedvar("R","Incorrect Message Type",f"{nope} Make sure you entered a channel ID, which should be an integer.",False))

                except ChannelDoesNotExist:
                    await ctx.send(embed=setembedvar("R","Channel does not exist",f"{nope} Make sure you entered the right channel ID.",False))

            print("Exited welcome message channel loop.")
            return shouldContinue, success1, welcomeChannel

        async def welcomeMessage():
            await ctx.send(embed=setembedvar("G","Welcome Message Setup","OK, now what's the welcome message?\nYou can use the placeholders {member} and {servername}.",False).set_footer(text="Or, enter `cancel` to cancel."))

            shouldContinue = False
            hasTimedOut = False
            cancelled = False
        
            while shouldContinue == False and hasTimedOut == False and cancelled == False:
                print("In welcome message loop.")
                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=welcomeMessageCheck)

                    if msg.content == "cancel":
                        cancelled = True
                        await ctx.send(embed=cancelledVar)
                    else:
                        welcomeMessage = msg.content
                        success2 = True
                        shouldContinue = True
                
                except asyncio.TimeoutError:
                    hasTimedOut = True
                    print("Setup timed out")
                    await ctx.send(embed=timedOutVar)

            return shouldContinue, success2, welcomeMessage

        shouldContinue = success1 = success2 = False

        while success1 == False and shouldContinue == False:
            shouldContinue, success1, welcomeChannel = await welcomeChannel()
        shouldContinue = False
        while success2 == False and shouldContinue == False:
            shouldContinue, success2, welcomeMessage = await welcomeMessage()
        member = author.mention
        servername = ctx.guild.name
        await ctx.send(embed=setembedvar("G","Setup Complete",f"{yep} All done! Below you can see a preview of your welcome message."+"\nIf you want to change anything, simply re-run the command (>welcomesetup).",False))
        tempwelcomeMessage = welcomeMessage.replace("{member}",member).replace("{servername}",servername)
        await ctx.send(str(tempwelcomeMessage))

        guildid = ctx.guild.id

        with sqlite3.connect('welcome.db') as db:
            cursor = db.cursor()
            welcomerow = cursor.execute("SELECT * FROM welcome WHERE guildid = ?",(guildid,))
            data = cursor.fetchone()
            if data is None:
                print("Doesn't exist in database")
                try:
                    cursor.execute("INSERT INTO welcome VALUES(?,?,?)",(guildid,welcomeChannel,welcomeMessage))
                    await ctx.send(embed=setembedvar("G","Success!",f"{tada_animated} Changes written to database.",False))
                    db.commit()
                    db.close()
                except:
                    print("Critical error.")
            else:
                print("Exists in database")
                welcomerow = cursor.execute("SELECT * FROM welcome WHERE guildid = ?",(guildid,))
                try:
                    for row in welcomerow:
                        if int(row[1]) != welcomeChannel:
                            print("Channel ID mismatch.")
                            cursor.execute("UPDATE welcome SET channelid = ? WHERE guildid = ?",(welcomeChannel,guildid))
                        if str(row[2]) != welcomeMessage:
                            print("Welcome Message mismatch.")
                            cursor.execute("UPDATE welcome SET message = ? WHERE guildid = ?",(welcomeMessage,guildid))
                        db.commit()
                        await ctx.send(embed=setembedvar("G","Success!",f"{tada_animated} Changes written to database.",False))
                except:
                    print("Failed.")
                    await ctx.send(embed=setembedvar("R","Uh oh!",f"{nope} Changes could not be written to database."+"\nContact @TechLife#6902 for assistance.",False))

    @commands.Cog.listener()
    async def on_member_join(self,member):
        with sqlite3.connect('welcome.db') as db:
            cursor = db.cursor()
            try:
                welcomerow = cursor.execute("SELECT * FROM welcome WHERE guildid = ?",(member.guild.id,))
                data = cursor.fetchone()
                if data is None:
                    print("")
                else:
                    welcomerow = cursor.execute("SELECT * FROM welcome WHERE guildid = ?",(member.guild.id,))
                    for row in welcomerow:
                        welcomeChannel = self.bot.get_channel(row[1])
                        welcomeMessage = row[2].replace("{member}",member.mention).replace("{servername}",member.guild.name)
                        await welcomeChannel.send(welcomeMessage)
            except:
                print("Couldn't send welcome message.")

def setup(bot):
    bot.add_cog(Join(bot))