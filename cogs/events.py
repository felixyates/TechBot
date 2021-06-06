import discord, json, datetime
from discord.ext import commands
from modules.getjson import loadServerJson
from modules.variables import botServersChannel, dmChannel
from modules.embedvars import setembedvar



async def servermessage(self, guild, type):

    serversChannel = self.bot.get_channel(botServersChannel)

    if type == "join":

        beginning = "+ Joined"

    elif type == "leave":

        beginning = "- Left"

    message = f"{beginning} server `{guild.name}` with `{guild.member_count}` members, owned by `{guild.owner.name}` (user ID `{guild.owner.id}`)."
    await serversChannel.send(message)



class Events(commands.Cog, name="events"):



    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        
        await servermessage(self, guild, "join")

        # adapted from these comments:

            # https://stackoverflow.com/a/64513681/14577385
            # https://stackoverflow.com/a/52281859/14577385

        # thank you ^_^

        with open('servers.json', 'r') as f:
            servers = json.load(f)

        guildID = str(guild.id)
        
        # initialising dictionaries

        server = {}
        welcome = {}
        slurdetector = {}
        music = {}
        textresponder = {}

        # assigning default values to dictionaries
            # 0 disables the feature

        welcome["enabled"] = 0
        welcome["message"] = "Welcome to the {servername} server, {member}!"
        welcome["channel"] = "1"

        slurdetector["enabled"] = 0
        slurdetector["channel"] = "1"

        music["enabled"] = 0
        music["channel"] = "1"

        textresponder["enabled"] = 0
        textresponder["triggers"] = ""

        server["prefix"] = ">"

        # adding previous dictionaries to server dictionary

        server["welcome"] = welcome
        server["slurdetector"] = slurdetector
        server["music"] = music
        server["textresponder"] = textresponder

        # adds server dictionary to servers dictionary

        servers[guildID] = server

        with open('servers.json', 'w') as f:
            json.dump(servers, f, indent=4)



    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        await servermessage(self, guild, "leave")

        with open('servers.json', 'r') as f:
            servers = json.load(f)

        guildID = str(guild.id)
 
        servers.pop(guildID)

        with open('servers.json', 'w') as f: # deletes the guild
            json.dump(servers, f, indent=4)



    @commands.Cog.listener()
    async def on_member_join(self,member):

        servers = loadServerJson()
        server = servers[str(member.guild.id)]
        welcome = server["welcome"]

        if welcome["enabled"] == 1:
            welcomeChannel = self.bot.get_channel(int(welcome["channel"]))
            welcomeMessage = welcome["message"].replace("{member}",member.mention).replace("{servername}",member.guild.name)
            await welcomeChannel.send(welcomeMessage)



    @commands.Cog.listener()
    async def on_message(self,message):
        
        if message.author.bot == False:
            
            if isinstance(message.channel, discord.channel.DMChannel):

                directMessageChannel = self.bot.get_channel(dmChannel)
                dmEmbed = discord.Embed(color = 0x00ff00, timestamp = datetime.datetime.utcnow(), description = message.content)
                dmEmbed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
                dmEmbed.set_footer(text = f"User ID: {message.author.id}")
                await directMessageChannel.send(embed = dmEmbed)



def setup(bot):
    bot.add_cog(Events(bot))