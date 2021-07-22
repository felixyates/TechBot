import random, discord, json
from discord.ext import commands
from discord.ext.commands import has_permissions
from modules.embedvars import setembedvar,requestedbyfooter
from modules.getjson import loadServerJson, get_prefix
from bot import commandWarning
from discord_slash import cog_ext
from modules.emoji import nope, loading

def converttostr(input_seq, separator):
   "Join all the strings in list"
   final_str = separator.join(input_seq)
   return final_str

def get_prefix(bot, message):
    with open("servers.json", "r") as f:
        servers = json.load(f)
    return servers[str(message.guild.id)]["prefix"]

class Other(commands.Cog, name="other"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if self.bot.user.mentioned_in(message) and message.author.bot == False and message.content[3:] == self.bot.user.mention[2:]:
            prefix = get_prefix(self, message)
            await message.reply(f"Hey, {message.author.mention}! My prefix for this server is `{prefix}`. Run `{prefix}help` for, you guessed it, help :)")

    @commands.command()
    async def hello(self,ctx):
        "Says 'world'"
        await ctx.reply("world", mention_author=False)
        await commandWarning(ctx)

    @commands.command()
    async def add(self,ctx, a : float, b : float):
        "Adds two numbers together."
        total = a + b
        if int(total) == total:
            await ctx.reply(f"{str(int(a))} + {str(int(b))} = {str(int(total))}", mention_author=False)
        else:
            await ctx.reply(f"{a} + {b} = {a + b}", mention_author=False)
        await commandWarning(ctx)

    @commands.command()
    async def ping(self,ctx):
        "Returns 'pong' if the bot is active"
        pingVar = discord.Embed(color=0xff0000,title="🏓 Pong!",description=f"TechBot's ping to Discord is **{round(self.bot.latency *1000)}** ms!")
        pingVar = requestedbyfooter(pingVar,ctx.message)
        await ctx.reply(embed=pingVar, mention_author=False)
        await commandWarning(ctx)

    @commands.command()
    async def help(self,ctx):
        
        techbotCmdsURL = "https://www.techlifeyt.com/techbot-commands"
        techlifeLinksURL = "https://www.techlifeyt.com/links"
        techlifeIconURL = "https://www.techlifeyt.com/wp-content/uploads/2020/04/cropped-TechLife-150x150-1.png"
        helpVarMsg = f"""Enter `/` to see all of TechBot's commands. Don't see them? [Reinvite the bot](https://techlifeyt.com/invite-techbot) or [join the support server](https://techlifeyt.com/techbot)."""

        helpVar = setembedvar("G","Commands",helpVarMsg,url=techbotCmdsURL,author="TechLife", author_url=techlifeLinksURL, author_icon=techlifeIconURL)
        helpVar.add_field(name = "Get Support", value="Need help, or want to report a bug? Join the [support server](https://www.techlifeyt.com/techbot) for help.")
        helpVar = requestedbyfooter(helpVar,ctx.message)
        await ctx.reply(embed=helpVar, mention_author=False)

    @commands.command()
    async def serverinfo(self, ctx):

        embed = setembedvar("G","Server Info",thumbnail=ctx.guild.icon_url)

        server = loadServerJson()[str(ctx.guild.id)]
        welcome = server["welcome"]
        music = server["music"]
        slurDetector = server["slurdetector"]
        textResponder = server["textresponder"]

        enabledList = []

        enabledList.append(welcome['enabled'])
        enabledList.append(music['enabled'])
        enabledList.append(slurDetector['enabled'])
        enabledList.append(textResponder['enabled'])

        for i in range(len(enabledList)):
            if enabledList[i] == 0:
                enabledList[i] = "`Disabled`"
            elif enabledList[i] == 1:
                enabledList[i] = "`Enabled`"

        moduleField = f"""Welcome: {enabledList[0]}
        Music: {enabledList[1]}
        Slur Detector: {enabledList[2]}
        Text Responder: {enabledList[3]}"""

        embed.add_field(name="Name", value=ctx.guild.name)
        embed.add_field(name="Members", value=ctx.guild.member_count)
        embed.add_field(name="Modules", value=moduleField, inline=False)
        embed = requestedbyfooter(embed,ctx.message)

        await ctx.reply(embed = embed, mention_author=False)

    @cog_ext.cog_slash(name="hello", description="Says 'world'")
    async def slash_hello(self,ctx):
        await ctx.send("world")

    add_options = [{"name":"a","description":"The first number.","type":4,"required":"true"},{"name":"b","description":"The second number.","type":4,"required":"true"}]
    @cog_ext.cog_slash(name="add", description="Adds two numbers together.", options=add_options)
    async def slash_add(self,ctx, a: float, b: float):
        total = a + b
        if int(total) == total:
            await ctx.send(str(int(total)))
        else:
            await ctx.send(a + b)

    @cog_ext.cog_slash(name="ping", description="Returns 'pong' if the bot is active")
    async def slash_ping(self,ctx):
        await ctx.send(f"🏓 Pong! TechBot's ping to Discord is **{round(self.bot.latency *1000)}** ms!")

    @cog_ext.cog_slash(name="help", description="Shows the help prompt.")
    async def slash_help(self,ctx):
        
        await ctx.send("Here you go!")
        techbotCmdsURL = "https://www.techlifeyt.com/techbot-commands"
        techlifeLinksURL = "https://www.techlifeyt.com/links"
        techlifeIconURL = "https://www.techlifeyt.com/wp-content/uploads/2020/04/cropped-TechLife-150x150-1.png"
        helpVarMsg = f"""The link above will take you to a table with all of TechBot's commands.
        The prefix for this server (`{ctx.guild.name}`) is `{get_prefix(self,ctx)}`"""

        helpVar = setembedvar("G","Commands",helpVarMsg,url=techbotCmdsURL,author="TechLife", author_url=techlifeLinksURL, author_icon=techlifeIconURL)
        helpVar.add_field(name = "Get Support", value="Need help, or want to report a bug? Join the [support server](https://www.techlifeyt.com/techbot) for help.")
        helpVar.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url = ctx.author.avatar_url)
        await ctx.message.channel.send(embed=helpVar)

    #serverinfo_options = [{"name":"serverid","description":"The ID of the server to provide information about.","type":4,"required":"false"}]
    @cog_ext.cog_slash(name="serverinfo", description="Provides info about the server, or, if given, the specified server.")
    async def slash_serverinfo(self, ctx, serverid = 0):

        await ctx.send(f"{loading}  Gathering server info, please be patient...")
        found = False

        if serverid == 0:

            try:
                guild = ctx.guild
                embed = setembedvar("G","Server Info",thumbnail=guild.icon_url)
                requestedserver = loadServerJson()[str(guild.id)]
                found = True
            except:
                found = False

        else:

            servers = loadServerJson()

            for server in servers:

                if server == serverid:

                    guild = await self.bot.fetch_guild(serverid)
                    embed = setembedvar("G","Server Info",thumbnail=guild.icon_url)
                    requestedserver = servers[server]
                    found = True
                    break

        if found == True:

            welcome = requestedserver["welcome"]
            music = requestedserver["music"]
            slurDetector = requestedserver["slurdetector"]
            textResponder = requestedserver["textresponder"]

            enabledList = []

            enabledList.append(welcome['enabled'])
            enabledList.append(music['enabled'])
            enabledList.append(slurDetector['enabled'])
            enabledList.append(textResponder['enabled'])

            for i in range(len(enabledList)):
                if enabledList[i] == 0:
                    enabledList[i] = "`Disabled`"
                elif enabledList[i] == 1:
                    enabledList[i] = "`Enabled`"

            moduleField = f"""Welcome: {enabledList[0]}
            Music: {enabledList[1]}
            Slur Detector: {enabledList[2]}
            Text Responder: {enabledList[3]}"""

            embed.add_field(name="Name", value=guild.name)
            try:
                members = guild.member_count
                embed.add_field(name="Members", value=members)
            except AttributeError:
                embed.add_field(name="Members", value="Cannot fetch members for remote guild.", inline=False)
            embed.add_field(name="Modules", value=moduleField, inline=False)
            embed.set_footer(text = f"Requested by {ctx.author.display_name}", icon_url = ctx.author.avatar_url)

            await ctx.send(embed = embed)

        else:

            await ctx.send(f"{nope} Couldn't find server info. Make sure the server ID is right and that I have been added in said server.")



def setup(bot):
    bot.add_cog(Other(bot))