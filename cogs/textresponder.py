import discord
from discord.ext import commands
from modules.getjson import loadServerJson, updateServerJson, thisServerJson 
from modules.embedvars import setembedvar
from modules.emoji import yep
from discord_slash import cog_ext

global updateServerCache
servers = loadServerJson()

# Command-related functions

def listresponders(ctx):
    "Prints the server's text responders."
    server = thisServerJson(str(ctx.guild.id))
    embed = setembedvar("G",f"Text Responders for {ctx.guild.name}")
    embed.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url = ctx.author.avatar_url)
    embed.add_field(name = "Format", value = "Type, Trigger, Response, Added By (ID)", inline = False)
    triggers = server["textresponder"]["triggers"]

    for trigger in triggers:

        responder = triggers[trigger]
        embed.add_field(name = trigger, value=f'{responder["type"]}, {trigger}, {responder["response"]}, {responder["added_by"]}', inline=False)

    return embed

async def updateServerCache():
    "Refreshes server cache after it is updated."
    global servers
    servers = loadServerJson()

async def textresponderClassic(command, ctx):

    unavailablemsg = f"""⚠ This command is now only available through slash commands.
    Try entering `/{command}`. If the command does not show up, try [authorizing TechBot to add slash commands](https://www.techlifeyt.com/invite-techbot), wait up to an hour and reload your Discord (Ctrl+R).
        
    If the command still doesn't work, join the [support server](https://www.techlifeyt.com/techbot) and I'll help you out."""
    embed = setembedvar("R","Command Unavailable",unavailablemsg)
    await ctx.reply(embed=embed, mention_author=False)

# Command functions

async def addresponder(self, ctx, type: int, trigger: str, response: str):

    valid = True

    guildid = ctx.guild.id
    await updateServerCache()
    server = servers[str(guildid)]

    triggers = server["textresponder"]["triggers"]

    for responder in triggers:

        if responder == trigger:
            valid = False
            await ctx.send(f"Responder already exists. Remove it using `/removeresponder {trigger}` to add it again.")
            break

    if valid == True:

        responder = {}
        responder["type"] = type
        responder["response"] = response
        responder["added_by"] = ctx.author.id
        triggers[trigger] = responder
        servers[str(guildid)]["textresponder"]["triggers"] = triggers

        updateServerJson(servers)
        await updateServerCache()

        await ctx.send("Added responder.")

async def removeresponder(self, ctx, responder: str):

    guildid = ctx.guild.id
    await updateServerCache()

    if responder == "":
        await ctx.send("You must enter a responder from the list below:")
        await ctx.send(embed=listresponders(ctx))
    
    triggers = servers[str(guildid)]["textresponder"]["triggers"]
    found = False

    for trigger in triggers:

        if trigger == responder:

            found = True
            triggers.pop(trigger)
            servers[str(guildid)]["textresponder"]["triggers"] = triggers
            updateServerJson(servers)
            await updateServerCache()
            await ctx.send("Removed responder.")
            break
    
    if found == False:
            await ctx.send("Responder not found. Enter a trigger from the following list to remove it:")
            await ctx.send(embed=listresponders(ctx))

async def textresponder(self, ctx, state: bool):

    servers = loadServerJson()
            
    if state == True:

        state = 1
        await ctx.send(embed = setembedvar("G","Text Responder Enabled",yep+" Successfully enabled text responder module.\nTechBot will now respond to set up text triggers."))

    elif state == False:

        state = 0
        await ctx.send(embed = setembedvar("G","Text Responder Disabled",yep+" Successfully disabled text responder module.\nTechBot will no longer respond to set up text triggers."))

    servers[str(ctx.guild.id)]["textresponder"]["enabled"] = state
    updateServerJson(servers)
    await updateServerCache()

# Slash command choices and options

addresponder_choices = [{"name":"Exact Match","value":1},{"name":"Contains","value":2},{"name":"Exact (Case Insensitive)","value":3},{"name":"Contains (Case Insensitive)","value":4}]
addresponder_options = [{"name":"type","description":"Type of text responder to add.","type":4,"choices":addresponder_choices,"required":"true"},{"name":"trigger","description":"The text you want to trigger the response.","type":3,"required":"true"},{"name":"response","description":"The response you want sent when triggered by the trigger.","type":3,"required":"true"}]
textresponder_choices = [{"name":"Enabled","value":1},{"name":"Disabled","value":0}]
textresponder_options = [{"name":"state","description":"State of the text responder module.","type":4,"choices":textresponder_choices,"required":"true"}]

class TextResponder(commands.Cog, name="textresponder"):
    """Allows for the creation, deletion, and handling of text responders.
    Members must have the `Manage Emojis` permission to create or delete responders.
    No special permissions are required for listing the server's text responders."""

    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        """Checks sent messages. If the message is one of the triggers in the database, it will send the specified response. If guild trigger matches, bot will send response.

        Type 1 - exact match, Type 2 - contains, Type 3 - exact (case insensitive), Type 4 - contains (case insensitive)"""

        try:

            server = servers[str(message.guild.id)]

        except:

            return

        if server["textresponder"]["enabled"] == 1 and message.author.bot == False:

            textresponder = server["textresponder"]
            triggers = textresponder["triggers"]

            send = False

            for trigger in triggers:

                if triggers[trigger]["type"] == 1:

                    if trigger == message.content:

                        send = True
                
                elif triggers[trigger]["type"] == 2:
                
                    if trigger in message.content:

                        send = True

                elif triggers[trigger]["type"] == 3:

                    if trigger.upper() == message.content.upper():

                        send = True  

                elif triggers[trigger]["type"] == 4:

                    if trigger.upper() in message.content.upper():

                        send = True
                
                if send == True:

                    await message.channel.send(triggers[trigger]["response"])
                    break

    # Add responder

    @cog_ext.cog_slash(name="addresponder", description="Adds the requested text responder for the server.", options=addresponder_options)
    @commands.has_permissions(manage_emojis=True)
    async def slash_addresponder(self, ctx, type, trigger, response):
        await addresponder(self, ctx, type, trigger, response)

    @commands.command(name="addresponder")
    @commands.has_permissions(manage_emojis=True)
    async def normal_addresponder(self, ctx):
        await textresponderClassic("addresponder", ctx)

    # Remove responder

    @cog_ext.cog_slash(name="removeresponder", description="Removes all responders with the given trigger")
    @commands.has_permissions(manage_emojis=True)
    async def slash_removeresponder(self, ctx, responder: str):
        await removeresponder(self, ctx, responder)

    @commands.command(name="removeresponder")
    @commands.has_permissions(manage_emojis=True)
    async def regular_removeresponder(self, ctx, responder: str):
        await removeresponder(self, ctx, responder)

    # List responders

    @cog_ext.cog_slash(name="responders", description="Retrieves and shows the server's text responders.")
    async def slash_responders(self,ctx):
        await ctx.send(embed=listresponders(ctx))
    
    @commands.command(name="responders")
    async def regular_responders(self,ctx):
        await ctx.reply(embed=listresponders(ctx), mention_author=False)
    
    # Turn on/off module

    @cog_ext.cog_slash(name="textresponder", description="Turn text responder module on/off", options = textresponder_options)
    @commands.has_permissions(administrator = True)
    async def slash_textresponder(self, ctx, state: bool):
        await textresponder(self, ctx, state)
    
    @commands.command(name="textresponder")
    @commands.has_permissions(administrator = True)
    async def regular_textresponder(self, ctx, state: bool):
        await textresponder(self, ctx, state)
        
def setup(bot):
    bot.add_cog(TextResponder(bot))