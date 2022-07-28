import discord, json
from discord.ext import commands
from discord.commands import slash_command
from modules import embs, db, emoji, srv

def converttostr(input_seq, separator):
   "Join all the strings in list"
   final_str = separator.join(input_seq)
   return final_str

class Other(commands.Cog, name = 'other'):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @slash_command(name="ping", description="Returns 'pong' if the bot is active")
    async def ping(self, ctx):
        await ctx.respond(f"🏓 Pong! TechBot's latency is **{round(self.bot.latency *1000)}** ms!")

    @slash_command(name="help", description="Shows the help prompt")
    async def help(self,ctx):
        await ctx.respond(embed = embs.Help(ctx.author))

    @slash_command(name="serverinfo", description="Provides info about the server, or, if given, the specified server")
    async def serverinfo(self, ctx,
        id: discord.Option(int, "ID of the server you want information about", default = 0)
    ):
        if id == 0:
            server = srv.Server(ctx.guild.id)
        else:
            server = srv.Server(id)

        try:
            await server.Fetch(self.bot)
        except Exception as e:
            await ctx.respond(embed = embs.Failure("I'm not in that server, sorry! Try again with a different ID", e))
            return

        embed = embs.Embed(title = "Server Info", thumbnail = server.icon.url)

        if (await server.Exists_DB()):
            moduleField = ""

            modules = await server.GetModules()
            for module in modules:
                module: srv.Server.Module
                if module.IsEnabled():
                    moduleField += f'{module.name}: Enabled'
                else:
                    moduleField += f'{module.name}: Disabled'

            embed.add_field(name="Name", value = server.name)
            if hasattr(server, 'approximate_member_count'):
                members = server.approximate_member_count
            else:
                members = "Cannot fetch members for remote guild."
            embed.add_field(name="Members", value= members)
            embed.add_field(name="Modules", value = moduleField, inline=False)
            embed.RequestedByFooter(ctx.author)
            await ctx.respond(embed = embed)
        else:
            await ctx.respond(embed = embs.Failure("Couldn't find server info. Make sure the server ID is right and that I have been added in said server."))

def setup(bot):
    bot.add_cog(Other(bot))