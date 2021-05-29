import discord
from discord.ext import commands
from modules.getjson import loadServerJson, updateServerJson, thisServerJson 
from modules.embedvars import setembedvar, requestedbyfooter
from modules.emoji import yep, nope

def listresponders(ctx):

    server = thisServerJson(str(ctx.guild.id))
    embed = setembedvar("G",f"Text Responders for {ctx.guild.name}")
    embed = requestedbyfooter(embed, ctx.message)
    embed.add_field(name = "Format", value = "Type, Trigger, Response, Added By (ID)", inline = False)
    triggers = server["textresponder"]["triggers"]

    for trigger in triggers:

        responder = triggers[trigger]
        embed.add_field(name = trigger, value=f'{responder["type"]}, {trigger}, {responder["response"]}, {responder["added_by"]}', inline=False)

    return embed

global updateServerCache

async def updateServerCache():

    global servers
    servers = loadServerJson()

servers = loadServerJson()

class TextResponder(commands.Cog, name="textresponder"):
    def __init__(self,bot):
        self.bot = bot

# Checks sent messages. If the message is one of the triggers in the database, it will send the specified response.

    @commands.Cog.listener()
    async def on_message(self,message):
        
        # Checks text responder database for guild triggers.
        # If guild trigger matches, bot will send response.
        # Type 1 - exact match, Type 2 - contains, Type 3 - contains (case insensitive), Type 4 - exact (case insensitive)

        server = servers[str(message.guild.id)]

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

                    if trigger.upper() in message.content.upper():

                        send = True
                
                elif triggers[trigger]["type"] == 4:

                    if trigger.upper() == message.content.upper():

                        send = True
                
                if send == True:

                    await message.channel.send(triggers[trigger]["response"])



    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def addresponder(self,ctx,type:int,request:str):
        ## Adds the requested text responder for the server. Use '_' for spaces and '=' to separate trigger and response.

        guildid = ctx.guild.id
        await updateServerCache()
        server = servers[str(guildid)]
        
        valid = True
        request = request.split('=')

        trigger,response = request[0],request[1]
        server = servers[str(guildid)]

        if trigger != "" and response != "":

            if type != 1 and type != 2 and type != 3 and type != 4:
                valid = False
                await ctx.send("Valid responder types: 1 (exact match), 2 (contains)")

            triggers = server["textresponder"]["triggers"]

            
            trigger = trigger.replace("_"," ")
            response = response.replace("_"," ")

            for responder in triggers:

                if responder == trigger:
                    valid = False
                    await ctx.send(f"Responder already exists. Remove it using `{server['prefix']}removeresponder {trigger}` to add it again.")
                    break

            if valid == True:

                responder = {}
                responder["type"] = type
                responder["response"] = response
                responder["added_by"] = ctx.message.author.id
                triggers[trigger] = responder
                servers[str(guildid)]["textresponder"]["triggers"] = triggers

                updateServerJson(servers)
                await updateServerCache()

                await ctx.send("Added responder.")
        
        else:
            
            errorMsg = f"""The responder **must** have *one* trigger, and *one* response that cannot be blank, and should separated by the equals (`=`) character, with spaces denoted by the underscore (`_`) character.

            Example: `{server["prefix"]}addresponder 1 hello=hello_world!`"""
            embed = setembedvar("R","Incorrect Command Syntax", errorMsg)
            embed.set_footer(text = f"Error triggered by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)
            await ctx.send(embed=embed)



    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def removeresponder(self,ctx,responder: str):
        ## Removes all responders with the given trigger

        guildid = ctx.guild.id
        await updateServerCache()

        if responder == "":
            await ctx.send("You must enter a responder from the list below:")
            await ctx.send(embed=listresponders(ctx))
            
        responder = responder.replace("_"," ")
        
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



    @commands.command()
    async def responders(self,ctx):
        ## Retrieves and shows the server's text responders.
        embedVar = listresponders(ctx)
        await ctx.send(embed=embedVar)

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



def setup(bot):
    bot.add_cog(TextResponder(bot))