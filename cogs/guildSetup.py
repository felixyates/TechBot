import discord, os, asyncio, sqlite3, json
from discord.ext import commands
from discord.ext.commands import has_permissions

class GuildSetup(commands.Cog, name="guildsetup"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        # adapted from these comments:
            # https://stackoverflow.com/a/64513681/14577385
            # https://stackoverflow.com/a/52281859/14577385
        # thank you :)

        with open('servers.json', 'r') as f:
            servers = json.load(f)

        guildID = str(guild.id)
        
        # initialising dictionaries

        server = {}
        welcome = {}
        slurdetector = {}
        music = {}

        # assigning default values to dictionaries
            # 0 disables the feature

        welcome["enabled"] = 0
        welcome["message"] = "Welcome to the {servername} server, {member}!"
        welcome["channel"] = "1"

        slurdetector["enabled"] = 0
        slurdetector["channel"] = "1"

        music["enabled"] = 0
        music["channel"] = "1"

        server["prefix"] = ">"

        # adding previous dictionaries to server dictionary

        server["welcome"] = welcome
        server["slurdetector"] = slurdetector
        server["music"] = music

        # adds server dictionary to servers dictionary

        servers[guildID] = server

        with open('servers.json', 'w') as f:
            json.dump(servers, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild): # when the bot is removed from a guild

        with open('servers.json', 'r') as f:
            servers = json.load(f)

        guildID = str(guild.id)
 
        servers.pop(guildID)

        with open('servers.json', 'w') as f: # deletes the guild
            json.dump(servers, f, indent=4)

def setup(bot):
    bot.add_cog(GuildSetup(bot))