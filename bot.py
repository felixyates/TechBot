import discord, os
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
from modules.embedvars import setembedvar
from modules.getjson import secret, get_prefix
from modules.variables import errorChannel
from cogs.administration import Cancelled as setup_cancelled

TOKEN = secret("discord")

intents = discord.Intents().all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=get_prefix, intents = intents)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(embed=setembedvar("R","Command Missing Argument(s)",f"`{str(error)}`"))
        return
    elif isinstance(error, setup_cancelled):
        return
    else:
        
        channel = bot.get_channel(errorChannel)

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

        await ctx.send(embed=public_embed)
        await channel.send(embed=embed)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)