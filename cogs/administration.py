import discord, os, asyncio, json
from discord.ext import commands
from discord.ext.commands import has_permissions
from modules.embedvars import setembedvar
from modules.emoji import yep, nope, tada_animated
from modules.getjson import loadServerJson, updateServerJson

class ChannelDoesNotExist(Exception):
    pass

class Cancelled(Exception):
    pass

def channelCheck(self, ctx, channelID):

    channelExists = False

    try:
        channelID = int(channelID)
    except ValueError:
        raise ValueError

    for guild in self.bot.guilds:
        if guild.id == ctx.guild.id:
            for channel in guild.text_channels:
                if channel.id == channelID:
                    channelExists = True
    
    return channelExists

def cancelcheck(m):
    # Checks if user desires to cancel setup.
    print(f"Entered cancelcheck with {m.content}")
    if m.content == "cancel":
        print("User cancelled setup.")
        return True
    else:
        print("User continuing with setup.")
        return False

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
        
def authorCheck(m):
    # Checks if message is from command issuer.
    if m.author.id == author.id:
        return True
    else:
        return False

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

class Administration(commands.Cog, name="administration"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def setprefix(self, ctx, prefix):

        # adapted from this comment: https://stackoverflow.com/a/64513681/14577385
        # thank you :)

        servers = loadServerJson()

        servers[str(ctx.guild.id)]["prefix"] = prefix
        updateServerJson(servers)
        
        await ctx.send(embed = setembedvar("G","Prefix changed",f"{yep} Successfully changed prefix to: {prefix}"))
        await ctx.message.guild.me.edit(nick=f"[{prefix}] TechBot")
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def music(self, ctx, state):

        servers = loadServerJson()
        server = servers[str(ctx.guild.id)]

        if server["music"]["channel"] != "1":

            if state == "on" or state == "off":
                
                if state == "on":

                    state = 1
                    await ctx.send(embed = setembedvar("G","Music Enabled",f"{yep} Successfully enabled music module."))

                elif state == "off":

                    state = 0
                    await ctx.send(embed = setembedvar("G","Music Disabled",f"{yep} Successfully disabled music module."))

                servers[str(ctx.guild.id)]["music"]["enabled"] = state
                updateServerJson(servers)

            else:

                await ctx.send(embed = setembedvar("R","Incorrect Syntax",f"{nope} Enter 'on' or 'off'."))
        
        else:

            await ctx.send(embed = setembedvar("R","Music Channel Unset",f"{nope} Set up the music module first ({server['prefix']}musicsetup <channel-id>)"))
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcomesetup(self,ctx):

        ## Allows for guild admins to create / set a custom welcome message for their server.
        ## Syntax: >welcomesetup
        ## Placeholders for message: {member} and {servername}

        global author
        author = ctx.author
        success1 = success2 = False

        prefix= loadServerJson()[str(ctx.guild.id)]["prefix"]

        timedOutVar = setembedvar("R","Setup Expired",f"{nope} Didn't receive response. Run `{prefix}welcomesetup` to restart setup.",False)

        cancelledMsg = f"""Cancelled welcome message setup.
                        You can always run {prefix}welcomesetup to start again."""
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
                            await ctx.send(embed=setembedvar("G","Channel exists",f"{yep} Channel set to <#{channelID}>.",False))
                            shouldContinue = True
                            success1 = True
                            return shouldContinue, success1, channelID

            if channelExists == False:
                raise ChannelDoesNotExist(f"Channel {channelID} not found.")

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
                        raise Cancelled
                    else:
                        shouldContinue, success1, welcomeChannel = await doesChannelExist(int(msg.content))
                        return shouldContinue, success1, welcomeChannel

                except asyncio.TimeoutError:
                    hasTimedOut = True
                    print("Setup timed out")
                    await ctx.send(embed=timedOutVar)
        
                except ValueError:
                    await ctx.send(embed=setembedvar("R","Incorrect Message Type",f"{nope} Make sure you entered a channel ID, which should be an integer.",))

                except ChannelDoesNotExist:
                    await ctx.send(embed=setembedvar("R","Channel does not exist",f"{nope} Make sure you entered the right channel ID.",))

            print("Exited welcome message channel loop.")

        async def welcomeMessage():
            await ctx.send(embed=setembedvar("G","Welcome Message Setup","OK, now what's the welcome message?\nYou can use the placeholders {member} and {servername}.",).set_footer(text="Or, enter `cancel` to cancel."))

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
        prefix= loadServerJson()[str(ctx.guild.id)]["prefix"]
        await ctx.send(embed=setembedvar("G","Setup Complete",f"{yep} All done! Below you can see a preview of your welcome message."+"\n"+f"If you want to change anything, simply re-run the command ({prefix}welcomesetup).",False))
        tempwelcomeMessage = welcomeMessage.replace("{member}",member).replace("{servername}",servername)
        await ctx.send(str(tempwelcomeMessage))

        guildid = ctx.guild.id

        servers = loadServerJson()
        server = servers[str(guildid)]
        server["welcome"]["enabled"] = 1
        server["welcome"]["channel"] = str(welcomeChannel)
        server["welcome"]["message"] = welcomeMessage
        servers[str(guildid)] = server
        updateServerJson(servers)
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def musicsetup(self, ctx, channelID):

        ## Allows guild admins to use the music module in their own server.
        ## Syntax: >musicsetup <music-channel-id>

        channelExists = False
        shouldContinue = True

        try:
            channelID = int(channelID)
        except ValueError:
            await ctx.send(embed=setembedvar("R","Incorrect Message Type",f"{nope} Make sure you entered a channel ID, which should be an integer."))
            shouldContinue = False

        for guild in self.bot.guilds:
            if guild.id == ctx.guild.id:
                for channel in guild.text_channels:
                    if channel.id == channelID:
                        channelExists = True
                        await ctx.send(embed=setembedvar("G","Channel exists",f"{yep} Music module enabled and channel set to <#{channelID}>."))
                        
                        servers = loadServerJson()
                        server = servers[str(guild.id)]
                        server["music"]["enabled"] = 1
                        server["music"]["channel"] = str(channelID)
                        servers[str(guild.id)] = server
                        updateServerJson(servers)

        if channelExists == False and shouldContinue == True:
            await ctx.send(embed=setembedvar("R","Channel does not exist",f"{nope} Make sure you entered the right channel ID."))
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def slurdetectorsetup(self, ctx, channelID):

        ## Allows guild admins to use the slur detector module in their own server.
        ## Syntax: >slurdetectorsetup <moderator-channel-id>

        try:

            channelExists = channelCheck(self, ctx, channelID)

            servers = loadServerJson()
            server = servers[str(ctx.guild.id)]
            server["slurdetector"]["enabled"] = 1
            server["slurdetector"]["channel"] = str(channelID)
            servers[str(ctx.guild.id)] = server
            updateServerJson(servers)

            if channelExists == True:
                await ctx.send(embed=setembedvar("G","Channel exists",f"{yep} Slur detector enabled and moderation channel set to <#{channelID}>."))

        except ValueError:
            await ctx.send(embed=setembedvar("R","Incorrect Message Type",f"{nope} Make sure you entered a channel ID, which should be an integer."))
            shouldContinue = False

        if channelExists == False and shouldContinue == True:
            await ctx.send(embed=setembedvar("R","Channel does not exist",f"{nope} Make sure you entered the right channel ID."))

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def slurdetector(self, ctx, state):

        servers = loadServerJson()
        server = servers[str(ctx.guild.id)]

        if server["slurdetector"]["channel"] != "1":

            if state == "on" or state == "off":
                
                if state == "on":

                    state = 1
                    await ctx.send(embed = setembedvar("G","Slur Detector Enabled",f"{yep} Successfully enabled slur detector module."))

                elif state == "off":

                    state = 0
                    await ctx.send(embed = setembedvar("G","Slur Detector Disabled",f"{yep} Successfully disabled slur detector module."))

                servers[str(ctx.guild.id)]["slurdetector"]["enabled"] = state
                updateServerJson(servers)

            else:

                await ctx.send(embed = setembedvar("R","Incorrect Syntax",f"{nope} Enter 'on' or 'off'."))
        
        else:

            await ctx.send(embed = setembedvar("R","Slur Detector Moderation Channel Unset",f"{nope} Set up the slur detector module first"+"\n"+f"({server['prefix']}slurdetectorsetup <channel-id>)"))
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def welcome(self, ctx, state):

        servers = loadServerJson()
        server = servers[str(ctx.guild.id)]

        if server["welcome"]["channel"] != "1":

            if state == "on" or state == "off":
                
                if state == "on":

                    state = 1
                    await ctx.send(embed = setembedvar("G","Welcome Module Enabled",f"{yep} Successfully enabled welcome module."))

                elif state == "off":

                    state = 0
                    await ctx.send(embed = setembedvar("G","Welcome Module Disabled",f"{yep} Successfully disabled welcome module."))

                servers[str(ctx.guild.id)]["welcome"]["enabled"] = state
                updateServerJson(servers)

            else:

                await ctx.send(embed = setembedvar("R","Incorrect Syntax",f"{nope} Enter 'on' or 'off'."))
        
        else:

            await ctx.send(embed = setembedvar("R","Welcome Channel Unset",f"{nope} Set up the welcome module first"+"\n"+f"({server['prefix']}welcomesetup)"))

def setup(bot):
    bot.add_cog(Administration(bot))