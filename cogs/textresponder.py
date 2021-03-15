import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
import sqlite3

def listresponders(ctx):
    guildid = int(ctx.guild.id)
    db = sqlite3.connect('textresponder.db')
    cursor = db.cursor()
    responders = cursor.execute("SELECT * FROM RESPONDERS WHERE guildid = ?",(guildid,))
    embedVar = discord.Embed(color=0x00ff00,title="Text Responders")
    embedVar.add_field(name="Format",value=f"Type, Trigger, Response, Added By", inline=False)
    for row in responders:
        embedVar.add_field(name=f"{row[2]}",value=f"{row[1]}, {row[2]}, {row[3]}, {row[4]}", inline=False)
    embedVar.set_footer(text=f"For guild {ctx.guild}.")
    db.close()
    return embedVar

class TextResponder(commands.Cog, name="textresponder"):
    def __init__(self,bot):
        self.bot = bot

# Checks sent messages. If the message is one of the triggers in the database, it will send the specified response.

    @commands.Cog.listener()
    async def on_message(self,message):
        if "nigg" in message.content:
            await message.channel.send("DO NOT SAY THAT!!! "+message.author.mention)
        db = sqlite3.connect('textresponder.db')
        cursor = db.cursor()
        guildid = message.guild.id
        responders = cursor.execute("SELECT * FROM RESPONDERS WHERE guildid = ?",(guildid,))
        if message.author.bot == False:
            for row in responders:
                if row[1] == 1:
                    if message.content == row[2]:
                        await message.channel.send(row[3])
                elif row[1] == 2:
                    if row[2] in message.content:
                        await message.channel.send(row[3])
        db.close()
    
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def addresponder(self,ctx,type:int,request:str): ## Adds the requested text responder for the server. Use '_' for spaces and '=' to separate trigger and response.

        guildid = ctx.guild.id
        db = sqlite3.connect('textresponder.db')
        print("Opened database successfully")
        cursor = db.cursor()
        valid = True
        request = request.split('=')
        print(f"Responder type {type}.")

        if type != 1 and type != 2:
            valid = False
            await ctx.send("Valid responder types: 1 (exact match), 2 (contains)")
        responders = cursor.execute("SELECT * FROM RESPONDERS WHERE guildid = ?",(guildid,))
        trigger,response = request[0],request[1]
        print(request,trigger,response)
        trigger = trigger.replace("_"," ")
        response = response.replace("_"," ")
        print(f"Added spaces: {trigger}, {response}")
        for row in responders:
            if row[2] == trigger:
                valid = False
                await ctx.send(f"Responder already exists. Remove it using >removeresponder {trigger} to add it again.")
                break

        if valid == True:
            print(trigger,response)
            requestedby = str(ctx.message.author)
            print(requestedby)
            print(guildid)
            try:
                cursor.execute("INSERT INTO RESPONDERS VALUES(?,?,?,?,?)",(guildid,type,trigger,response,requestedby))
                db.commit()
                print("Database changes committed successfully")
            except:
                db.close()
                print("Failed to add to database.")
            await ctx.send("Responder added.")

        db.close()
        print("Closed database successfully")
    
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def removeresponder(self,ctx,responder: str): ## Removes all responders with the given trigger
        guildid = ctx.guild.id
        db = sqlite3.connect('textresponder.db')
        print("Opened database successfully")
        cursor = db.cursor()
        if responder == "":
            await ctx.send("You must enter a responder from the list below:")
            await ctx.send(embed=listresponders(ctx))
        responder = responder.replace("_"," ")
        responders = cursor.execute("SELECT * FROM RESPONDERS WHERE guildid = ?",(guildid,))
        found = False
        for row in responders:
            if row[2] == responder:
                found = True
                print("Responder found.")
                cursor.execute("DELETE FROM RESPONDERS WHERE guildid = ? AND trigger = ?",(guildid,responder))
                await ctx.send(f"Removed responder '{responder}' successfully.")
                try:
                    db.commit()
                except:
                    print("Failed to write changes to database.")
        
        if found == False:
                await ctx.send("Responder not found. Enter a trigger from the following list to remove it:")
                await ctx.send(embed=listresponders(ctx))
        db.close()


    @commands.command() ## Retrieves and shows the server's text responders.
    async def responders(self,ctx):
        embedVar = listresponders(ctx)
        await ctx.send(embed=embedVar)

def setup(bot):
    bot.add_cog(TextResponder(bot))