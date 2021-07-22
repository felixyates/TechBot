import discord
from discord.ext import commands
from modules.getjson import loadServerJson, updateServerJson, thisServerJson 
from modules.embedvars import setembedvar, requestedbyfooter
from modules.emoji import yep, nope
from discord_slash import cog_ext
from bot import commandWarning

def listresponders(ctx):

    server = thisServerJson(str(ctx.guild.id))
    embed = setembedvar("G",f"Text Responders for {ctx.guild.name}")
    embed.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url = ctx.author.avatar_url)
    embed.add_field(name = "Format", value = "Type, Trigger, Response, Added By (ID)", inline = False)
    triggers = server["textresponder"]["triggers"]

    for trigger in triggers:

        responder = triggers[trigger]
        embed.add_field(name = trigger, value=f'{responder["type"]}, {trigger}, {responder["response"]}, {responder["added_by"]}', inline=False)

    return embed

global updateServerCache

async def updateServerCache():
    "Refreshes server cache after it is updated"

    global servers
    servers = loadServerJson()

servers = loadServerJson()

class TextResponder(commands.Cog, name="textresponder"):
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

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def addresponder(self,ctx):
        "Adds the requested text responder for the server. Use '_' for spaces and '=' to separate trigger and response."

        command = "addresponder"
        unavailablemsg = f"""⚠ This command is now only available through slash commands.

        Try entering `/{command}`. If the command does not show up, try [authorizing TechBot to add slash commands](https://www.techlifeyt.com/invite-techbot), wait up to an hour and reload your Discord (Ctrl+R).
        
        If the command still doesn't work, join the [support server](https://www.techlifeyt.com/techbot) and I'll help you out."""
        await ctx.send(embed = setembedvar("R","Command Unavailable",unavailablemsg))

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def removeresponder(self,ctx):
        "Removes all responders with the given trigger"

        command = "removeresponder"
        unavailablemsg = f"""⚠ This command is now only available through slash commands.

        Try entering `/{command}`. If the command does not show up, try [authorizing TechBot to add slash commands](https://www.techlifeyt.com/invite-techbot), wait up to an hour and reload your Discord (Ctrl+R).

        If the command still doesn't work, join the [support server](https://www.techlifeyt.com/techbot) and I'll help you out."""
        await ctx.send(embed = setembedvar("R","Command Unavailable",unavailablemsg))

    @commands.command()
    async def responders(self,ctx):
        ## Retrieves and shows the server's text responders.
        embedVar = listresponders(ctx)
        await ctx.send(embed=embedVar)
        await commandWarning(ctx)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def textresponder(self, ctx, state):

        servers = loadServerJson()

        if state == "on" or state == "off":
                
            if state == "on":

                state = 1
                await ctx.send(embed = setembedvar("G","Text Responder Enabled",yep+" Successfully enabled text responder module.\nTechBot will now respond to set up text triggers."))

            elif state == "off":

                state = 0
                await ctx.send(embed = setembedvar("G","Text Responder Disabled",yep+" Successfully disabled text responder module.\nTechBot will no longer respond to set up text triggers."))

            servers[str(ctx.guild.id)]["textresponder"]["enabled"] = state
            updateServerJson(servers)
            await updateServerCache()

        else:

            await ctx.send(embed = setembedvar("R","Incorrect Command Syntax",f"{nope} Enter 'on' or 'off'."))
        await commandWarning(ctx)

    addresponder_choices = [{"name":"Exact Match","value":1},{"name":"Contains","value":2},{"name":"Exact (Case Insensitive)","value":3},{"name":"Contains (Case Insensitive)","value":4}]
    addresponder_options = [{"name":"type","description":"Type of text responder to add.","type":4,"choices":addresponder_choices,"required":"true"},{"name":"trigger","description":"The text you want to trigger the response.","type":3,"required":"true"},{"name":"response","description":"The response you want sent when triggered by the trigger.","type":3,"required":"true"}]
    @cog_ext.cog_slash(name="addresponder", description="Adds the requested text responder for the server.", options=addresponder_options)
    @commands.has_permissions(manage_emojis=True)
    async def slashaddresponder(self,ctx,type:int, trigger:str, response:str):

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


    @cog_ext.cog_slash(name="removeresponder", description="Removes all responders with the given trigger")
    @commands.has_permissions(manage_emojis=True)
    async def slashremoveresponder(self,ctx,responder: str):

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



    @cog_ext.cog_slash(name="responders", description="Retrieves and shows the server's text responders.")
    async def slashresponders(self,ctx):
        embedVar = listresponders(ctx)
        await ctx.send(embed=embedVar)

    textresponder_choices = [{"name":"Enabled","value":1},{"name":"Disabled","value":0}]
    textresponder_options = [{"name":"state","description":"State of the text responder module.","type":4,"choices":textresponder_choices,"required":"true"}]
    @cog_ext.cog_slash(name="textresponder", description="Turn text responder module on/off", options = textresponder_options)
    @commands.has_permissions(administrator = True)
    async def slashtextresponder(self, ctx, state: bool):

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

def setup(bot):
    bot.add_cog(TextResponder(bot))