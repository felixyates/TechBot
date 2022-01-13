import discord, asyncio, discord_slash
from discord.ext import commands
from discord.ext.commands import has_permissions
from modules.embedvars import setembedvar
from modules.emoji import yep, nope
from modules.getjson import loadServerJson, updateServerJson
from discord_slash import cog_ext

# Errors

class ChannelDoesNotExist(Exception):
    pass

class Cancelled(Exception):
    pass

# Check functions

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
    "Checks if user desires to cancel setup."
    if m.content == "cancel":
        return True
    else:
        return False

def welcomeMessageCheck(m):
    """Checks if message is:
        a) from command issuer, or
        b) requesting cancellation"""
    if authorCheck(m) == True:
        cancelled = cancelcheck(m)
        if cancelled == True:
            return "cancel"
        else:
            return m.content
    else:
        print("Message not from command issuer.")
        
def authorCheck(m):
    "Checks if message is from command issuer."
    if m.author.id == author.id:
        return True
    else:
        return False

def channelIDcheck(m):
    """Checks if message is:
        a) from command issuer,
        b) requesting cancellation, or
        c) an integer"""
    if authorCheck(m) == True:
        cancelled = cancelcheck(m)
        if cancelled == True:
            return "cancel"
        elif cancelled == False:
            try:
                return int(m.content)
            except:
                raise ValueError
    else:
        print("Message not from command issuer.")

# Command functions

async def set_prefix(ctx, prefix):

    # adapted from this comment: https://stackoverflow.com/a/64513681/14577385
    # thank you :)

    servers = loadServerJson()

    servers[str(ctx.guild.id)]["prefix"] = prefix
    updateServerJson(servers)
    embed = setembedvar("G","Prefix changed",f"{yep} Successfully changed prefix to: {prefix}")

    if isinstance(ctx, discord_slash.context.SlashContext):

        await ctx.send(embed = embed)

    else:

        await ctx.reply(embed = embed, mention_author=False)
    
    await ctx.message.guild.me.edit(nick=f"[{prefix}] TechBot")

async def music_status(ctx, state):

    servers = loadServerJson()
    server = servers[str(ctx.guild.id)]

    if server["music"]["channel"] != "1":

        if state == "on" or state == "off":
            
            if state == "on":

                state = 1
                message = "enabled"

            elif state == "off":

                state = 0
                message = "disabled"

            if isinstance(ctx, discord_slash.context.SlashContext):

                await ctx.send(embed = setembedvar("G",f"Music {message}",f"{yep} Successfully {message} music module."))
            
            else:

                await ctx.reply(embed = setembedvar("G",f"Music {message}",f"{yep} Successfully {message} music module."), mention_author=False)


            servers[str(ctx.guild.id)]["music"]["enabled"] = state
            updateServerJson(servers)

        else:

            await ctx.reply(embed = setembedvar("R","Incorrect Syntax",f"{nope} Enter `on` or `off`."), mention_author=False)
    
    else:

        await ctx.send(embed = setembedvar("R","Music Channel Unset",f"{nope} Set up the music module first ({server['prefix']}musicsetup <channel-id>)"))

async def music_setup(self, ctx, channel):

    """Allows guild admins to use the music module in their own server.
    Syntax: >musicsetup <music-channel-id>"""

    channelExists = False
    shouldContinue = True

    if isinstance(channel, discord.channel.TextChannel):

        servers = loadServerJson()
        server = servers[str(ctx.guild.id)]
        server["music"]["enabled"] = 1
        server["music"]["channel"] = str(channel.id)
        servers[str(ctx.guild.id)] = server
        updateServerJson(servers)
        await ctx.send(embed=setembedvar("G","Channel exists",f"{yep} Music module enabled and channel set to <#{channel.id}>."))

    else:

        channelID = int(channel)

        for guild in self.bot.guilds:
            if guild.id == ctx.guild.id:
                for channel in guild.text_channels:
                    if channel.id == channelID:
                        channelExists = True
                        await ctx.reply(embed=setembedvar("G","Channel exists",f"{yep} Music module enabled and channel set to <#{channelID}>."), mention_author=False)
                        
                        servers = loadServerJson()
                        server = servers[str(guild.id)]
                        server["music"]["enabled"] = 1
                        server["music"]["channel"] = str(channelID)
                        servers[str(guild.id)] = server
                        updateServerJson(servers)

        if channelExists == False and shouldContinue == True:
            await ctx.reply(embed=setembedvar("R","Channel does not exist",f"{nope} Make sure you entered the right channel ID."), mention_author=False)

async def welcome_status(self, ctx, state):

    servers = loadServerJson()
    server = servers[str(ctx.guild.id)]

    if server["welcome"]["channel"] != "1":

        if state == "on" or state == "off":
            
            if state == "on":

                state = 1
                message = "enabled"

            elif state == "off":

                state = 0
                message = "disabled"

            embed = setembedvar("G",f"Welcome module {message}",f"{yep} Successfully {message} welcome module.")

            if isinstance(ctx, discord_slash.context.SlashContext):

                await ctx.send(embed = embed)

            else:

                await ctx.reply(embed = embed, mention_author=False)

            servers[str(ctx.guild.id)]["welcome"]["enabled"] = state
            updateServerJson(servers)

        else:

            await ctx.send(embed = setembedvar("R","Incorrect Syntax",f"{nope} Enter 'on' or 'off'."))
    
    else:

        await ctx.send(embed = setembedvar("R","Welcome Channel Unset",f"{nope} Set up the welcome module first"+"\n"+f"({server['prefix']}welcomesetup)"))

async def welcome_setup(self,ctx):

    """Allows for guild admins to create / set a custom welcome message for their server.
    Placeholders for message: `{member}` and `{servername}`
    Syntax: `>welcomesetup`"""

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
        "Checks to see if channel exists in guild."

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

        """Prompts user to give channel ID and waits for response or until timeout.
        Then checks message and to see if channel exists. Keeps waiting if user enters wrong format message or wrong channel ID."""

        shouldContinue = hasTimedOut = cancelled = success1 = False
    
        while shouldContinue == False and hasTimedOut == False and cancelled == False:
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
                await ctx.send(embed=timedOutVar)
    
            except ValueError:
                await ctx.send(embed=setembedvar("R","Incorrect Message Type",f"{nope} Make sure you entered a channel ID, which should be an integer.",))

            except ChannelDoesNotExist:
                await ctx.send(embed=setembedvar("R","Channel does not exist",f"{nope} Make sure you entered the right channel ID.",))

    async def welcomeMessage():
        await ctx.send(embed=setembedvar("G","Welcome Message Setup","OK, now what's the welcome message?\nYou can use the placeholders {member} and {servername}.",).set_footer(text="Or, enter `cancel` to cancel."))

        shouldContinue = False
        hasTimedOut = False
        cancelled = False
    
        while shouldContinue == False and hasTimedOut == False and cancelled == False:
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

async def slurdetector_status(self, ctx, state):

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

async def slurdetector_setup(self, ctx, channelID):

    """Allows guild admins to use the slur detector module in their own server.
    Syntax: >slurdetectorsetup <moderator-channel-id>"""

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

# Slash command choices and options

state_choices = [{"name":"On","value":"on"},{"name":"Off","value":"off"}]
state_options = [{"name":"state","description":"Whether the module is on or off.","type":3,"choices":state_choices,"required":"true"}]
musicsetup_options = [{"name":"channel","description":"The channel for the module to be active in.","type":7,"required":"true"}]
slurdetectorsetup_options = [{"name":"channel","description":"The channel for the module to be active in.","type":7,"required":"true"}]

class Administration(commands.Cog, name="administration"):

    def __init__(self, bot):
        self.bot = bot
    
    # Set prefix

    @cog_ext.cog_slash(name="setprefix", description="Sets the bot's prefix.")
    @commands.has_permissions(administrator = True)
    async def slash_set_prefix(self, ctx, prefix):
        await set_prefix(ctx, prefix)

    @commands.command(name="setprefix")
    @commands.has_permissions(administrator = True)
    async def regular_set_prefix(self, ctx, prefix):
        await set_prefix(ctx, prefix)

    # Music module

    @cog_ext.cog_subcommand(name="status", base="music", description="Turns the music module on/off.", options=state_options)
    @commands.has_permissions(administrator = True)
    async def slash_music_status(self, ctx, state):
        await music_status(ctx, state)

    @commands.command(name="music")
    @commands.has_permissions(administrator = True)
    async def regular_music_status(self, ctx, state):
        await music_status(ctx, state)

    @cog_ext.cog_subcommand(name="setup", base="music", description="Sets the server's music channel.", options=musicsetup_options)
    @commands.has_permissions(administrator = True)
    async def slash_music_setup(self, ctx, channel):
        await music_setup(self, ctx, channel)

    @commands.command(name="musicsetup")
    @commands.has_permissions(administrator = True)
    async def regular_music_setup(self, ctx, channel):
        await music_setup(self, ctx, channel)

    # Welcome module

    @cog_ext.cog_subcommand(name="setup", base="welcome", description="Sets the server's welcome channel.")
    @commands.has_permissions(administrator=True)
    async def slash_welcome_setup(self, ctx):
        await welcome_setup(self, ctx)

    @cog_ext.cog_subcommand(name="status", base="welcome", description="Turns the welcome message on/off.", options=state_options)
    @commands.has_permissions(administrator = True)
    async def slash_welcome_status(self, ctx, state):
        await welcome_status(self, ctx, state)

    # Slur detector module

    @cog_ext.cog_subcommand(name="status", base="slurdetector", description="Turns the slur detector on/off.", options=state_options)
    @commands.has_permissions(administrator = True)
    async def slash_slurdetector_status(self, ctx, state):
        await slurdetector_status(self, ctx, state)

    @cog_ext.cog_subcommand(name="setup", base="slurdetector", description="Sets the slur detector moderation channel.", options=slurdetectorsetup_options)
    @commands.has_permissions(administrator = True)
    async def slash_slurdetector_setup(self, ctx, channel):
        await slurdetector_setup(self, ctx, channel.id)

def setup(bot):
    bot.add_cog(Administration(bot))