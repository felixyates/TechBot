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
        # If guild trigger matches [Type 1] (/contains [Type 2]) message, bot will send response.
        # Type 1 - exact match, Type 2 - contains

        server = servers[str(message.guild.id)]

        if server["textresponder"]["enabled"] == 1:

            textresponder = server["textresponder"]
            triggers = textresponder["triggers"]

            for trigger in triggers:

                if triggers[trigger]["type"] == 1:

                    if trigger == message.content:

                        await message.channel.send(triggers[trigger]["response"])
                
                elif triggers[trigger]["type"] == 2:
                
                    if trigger in message.content:

                        await message.channel.send(triggers[trigger]["response"])

    
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def addresponder(self,ctx,type:int,request:str):
        ## Adds the requested text responder for the server. Use '_' for spaces and '=' to separate trigger and response.

        guildid = ctx.guild.id
        
        valid = True
        request = request.split('=')

        if type != 1 and type != 2:
            valid = False
            await ctx.send("Valid responder types: 1 (exact match), 2 (contains)")

        await updateServerCache()
        server = servers[str(guildid)]
        triggers = server["textresponder"]["triggers"]

        trigger,response = request[0],request[1]
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
                await ctx.send(embed = setembedvar("G","Welcome Module Enabled",f"{yep} Successfully enabled text responder module."))

            elif state == "off":

                state = 0
                await ctx.send(embed = setembedvar("G","Welcome Module Disabled",f"{yep} Successfully disabled text responder module."))

            servers[str(ctx.guild.id)]["textresponder"]["enabled"] = state
            updateServerJson(servers)
            await updateServerCache()

        else:

            await ctx.send(embed = setembedvar("R","Incorrect Syntax",f"{nope} Enter 'on' or 'off'."))

def setup(bot):
    bot.add_cog(TextResponder(bot))