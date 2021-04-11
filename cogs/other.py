import sqlite3, random, discord, os, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar

def converttostr(input_seq, separator):
   # Join all the strings in list
   final_str = separator.join(input_seq)
   return final_str

class Other(commands.Cog, name="other"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self,ctx):
        "Says 'world'"
        await ctx.send("world")

    @commands.command()
    async def add(self,ctx, left : int, right : int):
        "Adds two numbers together."
        await ctx.send(left + right)

    @commands.command()
    async def servers(self,ctx):
        "Lists some cool beans servers you should join"
        serversVar = discord.Embed(color=0x00ff00,title="Servers",description="Here are some pretty cool beans servers you should join")
        serversVar.add_field(name="Gaming Servers",value="[The Dead One](https://discord.gg/wWdr9bf)\n[The Active One](https://discord.gg/mgwgcubfnk)")
        serversVar.add_field(name="The Dev's Server",value="[TechLife](https://discord.gg/uzyeYFN)", inline=False)
        await ctx.message.channel.send(embed=serversVar)

    @commands.command()
    async def ping(self,ctx):
        "Returns 'pong' if the bot is active"
        pingVar = discord.Embed(color=0xff0000,title="🏓 Pong!",description=f"Your ping is **{round(self.bot.latency *1000)}** ms!")
        await ctx.send(embed=pingVar)

    @commands.command()
    async def help(self,ctx):
        helpVar=discord.Embed(title="Commands", url="https://www.techlifeyt.com/techbot-commands", description="The link above will take you to a table with all of TechBot's commands.\nThe default command prefix is >", color=0x00ff00)
        helpVar.set_author(name="TechLife", url="https://www.techlifeyt.com/links", icon_url="https://www.techlifeyt.com/wp-content/uploads/2020/04/cropped-TechLife-150x150-1.png")
        randomNumber = random.randint(1,4)
        if randomNumber == 1:
            helpVar.add_field(name="Join the developer's server!", value="[Click here](https://www.techlifeyt.com/discord)", inline=False)
        elif randomNumber == 2:
            helpVar.add_field(name="Support TechBot", value="[Patreon](https://www.techlifeyt.com/patreon)", inline=False)
        elif randomNumber == 3:
            helpVar.add_field(name="Are you subscribed?", value="[YouTube](https://www.techlifeyt.com/youtube)", inline=False)
        elif randomNumber == 4:
            helpVar.add_field(name="Do you like Minecraft?", value="[Check out the TechSMP](https://www.techlifeyt.com/techsmp)", inline=False)    
        await ctx.message.channel.send(embed=helpVar)

def setup(bot):
    bot.add_cog(Other(bot))