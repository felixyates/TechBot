import sqlite3, random, discord, os, asyncio, json
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar,requestedbyfooter
from modules.getjson import loadServerJson, get_prefix

def converttostr(input_seq, separator):
   # Join all the strings in list
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
        if self.bot.user.mentioned_in(message):
            prefix = get_prefix(self, message)
            await message.channel.send(f"Hey, {message.author.mention}! My prefix for this server is `{prefix}`. Run `{prefix}help` for, you guessed it, help :)")

    @commands.command()
    async def hello(self,ctx):
        "Says 'world'"
        await ctx.send("world")

    @commands.command()
    async def add(self,ctx, a : float, b : float):
        "Adds two numbers together."
        total = a + b
        if int(total) == total:
            await ctx.send(str(int(total)))
        else:
            await ctx.send(a + b)

    @commands.command()
    async def servers(self,ctx):
        "Lists some cool beans servers you should join"
        serversVar = discord.Embed(color=0x00ff00,title="Servers",description="Here are some pretty cool beans servers you should join")
        serversVar.add_field(name="Gaming Servers",value="[The Dead One](https://discord.gg/wWdr9bf)\n[The Active One](https://discord.gg/VQ6XBy9hZ8)")
        serversVar.add_field(name="The Dev's Server",value="[TechLife](https://techlifeyt.com/discord)", inline=False)
        serversVar = requestedbyfooter(serversVar,ctx.message)
        await ctx.message.channel.send(embed=serversVar)

    @commands.command()
    async def ping(self,ctx):
        "Returns 'pong' if the bot is active"
        pingVar = discord.Embed(color=0xff0000,title="🏓 Pong!",description=f"TechBot's ping to Discord is **{round(self.bot.latency *1000)}** ms!")
        pingVar = requestedbyfooter(pingVar,ctx.message)
        await ctx.send(embed=pingVar)

    @commands.command()
    async def help(self,ctx):
        
        techbotCmdsURL = "https://www.techlifeyt.com/techbot-commands"
        techlifeLinksURL = "https://www.techlifeyt.com/links"
        techlifeIconURL = "https://www.techlifeyt.com/wp-content/uploads/2020/04/cropped-TechLife-150x150-1.png"
        helpVarMsg = f"""The link above will take you to a table with all of TechBot's commands.
        The prefix for this server (`{ctx.guild.name}`) is `{get_prefix(self,ctx)}`"""

        helpVar = setembedvar("G","Commands",helpVarMsg,url=techbotCmdsURL,author="TechLife", author_url=techlifeLinksURL, author_icon=techlifeIconURL)
        randomNumber = random.randint(1,4)
        if randomNumber == 1:
            helpVar.add_field(name="Join the developer's server!", value="[Click here](https://www.techlifeyt.com/discord)", inline=False)
        elif randomNumber == 2:
            helpVar.add_field(name="Support TechBot", value="[Patreon](https://www.techlifeyt.com/patreon)", inline=False)
        elif randomNumber == 3:
            helpVar.add_field(name="Are you subscribed?", value="[YouTube](https://www.techlifeyt.com/youtube)", inline=False)
        elif randomNumber == 4:
            helpVar.add_field(name="Do you like Minecraft?", value="[Check out the TechSMP](https://www.techlifeyt.com/techsmp)", inline=False)
        helpVar = requestedbyfooter(helpVar,ctx.message)
        await ctx.message.channel.send(embed=helpVar)
    
    @commands.command()
    async def serverinfo(self, ctx):

        embed = setembedvar("G","Server Info",thumbnail=ctx.guild.icon_url)

        server = loadServerJson()[str(ctx.guild.id)]
        welcome = server["welcome"]
        music = server["music"]
        slurDetector = server["slurdetector"]

        enabledList = []

        enabledList.append(welcome['enabled'])
        enabledList.append(music['enabled'])
        enabledList.append(slurDetector['enabled'])

        for i in range(len(enabledList)):
            if enabledList[i] == 0:
                enabledList[i] = "`Disabled`"
            elif enabledList[i] == 1:
                enabledList[i] = "`Enabled`"

        moduleField = f"""Welcome: {enabledList[0]}
        Music: {enabledList[1]}
        Slur Detector: {enabledList[2]}"""

        embed.add_field(name="Name", value=ctx.guild.name)
        embed.add_field(name="Members", value=ctx.guild.member_count)
        embed.add_field(name="Modules", value=moduleField, inline=False)
        embed = requestedbyfooter(embed,ctx.message)

        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Other(bot))