import discord, os
from discord.ext import commands
from modules.getjson import secret, get_prefix
from discord_slash import SlashCommand

TOKEN = secret("discord")

intents = discord.Intents().all()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=get_prefix, intents = intents)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

commandWarningEmbed = discord.Embed(title="Notice: Classic Commands are Going Away", description="Classic commands are being replaced in favour of slash commands. Try typing `/` to see all of TechBot's commands and their descriptions. Don't see them? Try granting the bot [slash permissions](https://techlifeyt.com/invite-techbot), or join the [support server](https://techlifeyt.com/techbot).")

async def commandWarning(ctx):

    await ctx.reply(embed=commandWarningEmbed, mention_author=False)

bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)