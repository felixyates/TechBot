import discord, json, datetime
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from cogs.administration import Cancelled as setup_cancelled
from modules.getjson import loadServerJson
from modules.variables import botServersChannel, dmChannel, errorChannel
from modules.embedvars import setembedvar
from modules.emoji import nope

description = "Thank you for adding TechBot. If you run into any errors, or need any help, please make sure to join the [support server](https://techlifeyt.com/techbot)."
welcomeEmbed = discord.Embed(title = "Heeeere's TechBot!", description = description)
welcomeEmbed.set_author(name = "TechLife", icon_url = "https://www.techlifeyt.com/wp-content/uploads/2021/06/TechLife-PFP-128x.gif", url = "https://techlifeyt.com/links")

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
        await guild.text_channels[1].send(embed = welcomeEmbed)

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
        textresponder["triggers"] = {}

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

                if message.attachments:

                    for attachment in message.attachments:

                        attachmentEmbed.set_image(attachment.url)
                        attachmentEmbed = discord.Embed(color = 0x00ff00, timestamp = datetime.datetime.utcnow(), description = f"Attachment {attachment} of {len(message.attachments)} in message {message.id}")
                        attachmentEmbed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
                        attachmentEmbed.set_footer(text = f"User ID: {message.author.id}")
                        await directMessageChannel.send(embed = attachmentEmbed)                

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, ex):
        if isinstance(ex, discord.ext.commands.errors.MissingPermissions):
            await ctx.send(f"{nope} {ex}")
        elif isinstance(ex, discord.ext.commands.errors.NotOwner):
            await ctx.send(f"{nope} Hey! This command is for bot owners only.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, MissingRequiredArgument):
            await ctx.reply(embed=setembedvar("R","Command Missing Argument(s)",f"`{str(error)}`"), mention_author=False)
            return
        elif isinstance(error, setup_cancelled):
            return
        else:
            
            channel = self.bot.get_channel(errorChannel)

            if isinstance(ctx.channel, discord.channel.DMChannel):

                guildName = "Private DM"
                guildID = "N/A"
            
            else:

                guildName = ctx.guild.name
                guildID = ctx.guild.id

            embed = setembedvar("R","An Error Occurred")
            embed.add_field(name="Command Issuer", value=f"`{ctx.author.name} // {ctx.author.id}`")
            embed.add_field(name="Message", value=f"`{ctx.message.content}`")
            embed.add_field(name="Guild Name", value=f"`{guildName}`")
            embed.add_field(name="Guild ID", value=f"`{guildID}`")
            embed.add_field(name="Channel ID", value=f"`{ctx.channel.id}`")
            embed.add_field(name="Error Contents", value=f"`{str(error)}`", inline=False)

            public_embed = setembedvar("R","An Error Occurred")
            public_embed.add_field(name="Error Contents", value=f"`{str(error)}`", inline=False)
            public_embed.add_field(name="Get Support", value="Need help, or want to report a bug? Join the [support server](https://www.techlifeyt.com/techbot) for help.", inline = False)
            public_embed.set_footer(text = f"Error triggered by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar_url)

            await ctx.reply(embed=public_embed, mention_author=False)
            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Events(bot))