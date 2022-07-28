import discord, os
from discord.ext import commands
from discord.ext.tasks import loop
from discord.commands import SlashCommandGroup, slash_command
from asyncio import sleep
from modules import embs, emoji, getjson, vars, db, srv

maintenanceStatus = 0

class EchoModal(discord.ui.Modal):
    def __init__(self, title, *args, **kwargs) -> None:
        super().__init__(title, *args)

        self.add_item(discord.ui.InputText(label="Message", placeholder = "What you want the bot to send", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.children[0].value)

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @loop(seconds=60)
    async def status_update(bot: discord.Bot):
        DELAY = 60 # seconds
        if maintenanceStatus == 0:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for /help"))
            await sleep(DELAY)
            guildCount = await Owner.get_status_info(bot, 0)
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{guildCount} servers"))
            await sleep(DELAY)
            memberCount = await Owner.get_status_info(bot, 1)
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{memberCount} members"))
            await sleep(DELAY)

    async def get_status_info(bot: discord.Bot,mode):
        memberCount = guildCount = 0
        guilds = bot.fetch_guilds()
        async for guild in guilds:
            guild = bot.get_guild(guild.id)
            memberCount += guild.approximate_member_count
            guildCount += 1
        if mode == 0: # guildCount
            return guildCount
        return memberCount

    botCommands = SlashCommandGroup(
        "bot",
        "Commands related to the bot's function. Can only be run by its owner",
        guild_ids = vars.OWNERGUILDS
    )

    statusCommands = botCommands.create_subgroup("status", "Change the bot's status with these")
    serverCommands = botCommands.create_subgroup("server", "Handles server-related commands")
    state_choices = [discord.OptionChoice(name = 'On', value = 1), discord.OptionChoice(name = 'Off', value = 0)]

    @statusCommands.command(description = "Enables/disables the bot's maintenance status")
    @commands.is_owner()
    async def maintenance(self, ctx, status: discord.Option(
        int, description = "Whether maintenance mode is on or off", choices = state_choices
        )
    ):
        global maintenanceStatus
        maintenanceStatus = status
        if status == 1:
            channel = self.bot.get_channel(vars.STATUSCHANNEL)
            await channel.send(embed = embs.Maintenance())
            await ctx.respond(embed = embs.Success("Maintenance mode enabled"))
            await self.bot.change_presence(
                status = discord.Status.dnd,
                activity = discord.Activity(
                    type = discord.ActivityType.watching,
                    name = "for updates. The bot is currently undergoing maintenance and so some (if not all) commands will be unavailable."
                )
            )
            Owner.status_update.cancel()
        else:
            Owner.status_update.start(self.bot)
            await ctx.respond(embed = embs.Success("Maintenance mode disabled"))
            channel = self.bot.get_channel(vars.statusChannel)
            await channel.send(embed = embs.Online())

    @botCommands.command(description = "Lists the bot's servers and their module status")
    @commands.is_owner()
    async def servers(self, ctx):
        await ctx.respond(
            embed = discord.Embed(
                title = "Getting all servers...",
                description = f"""{emoji.loading} Hold on, this could take a while!
                Discord will be ratelimiting these messages..."""
            )
        )
        servers = await db.loadServers(self.bot)
        for server in servers: 
            await ctx.send(embed = await server.GetEmbed())
    
    @serverCommands.command(description = "Makes the bot leave the specified server")
    @commands.is_owner()
    async def leave(self, ctx, id: discord.Option(str, "ID of the server to leave")):
        to_leave: discord.Guild = await self.bot.fetch_guild(int(id))
        await to_leave.leave()

    status_types = [
        discord.OptionChoice(name = 'Playing'),
        discord.OptionChoice(name = 'Streaming'),
        discord.OptionChoice(name = 'Listening'),
        discord.OptionChoice(name = 'Watching')
    ]

    @statusCommands.command(description = "Set the bot's status")
    @commands.is_owner()
    async def set(self, ctx,
        type = discord.Option(
            str, description = "The type of status to start the status with", choices = status_types
        ),
        status = discord.Option(str, description = "The status to change the bot to", default = "")
    ):
        global maintenanceStatus
        if status != "":
            try:
                if type == "Playing":
                    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = status))
                elif type == "Listening":
                    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = status))
                elif type == "Watching":
                    await self.bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = status))
                elif type == "Streaming":
                    await self.bot.change_presence(activity = discord.Streaming(url = vars.streamingURL, name = status))

                maintenanceStatus = 1
                Owner.status_update.cancel()
                await ctx.respond(embed = embs.Success(f"Changed status to `{status}`"))
            except Exception as e:
                await ctx.respond(embed = embs.Failure("Couldn't update status", e))
        else:
            maintenanceStatus = 0

            if Owner.status_update.is_running() == True:
                Owner.status_update.restart(self.bot)
                description = "Restarted status cycle"
            else:
                Owner.status_update.start(self.bot)
                description = "Started status cycle"
            
            await ctx.respond(embed = embs.Success(description, title = "Reset Status"))

    @botCommands.command(description = "Logs the bot out of Discord")
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.respond(embed = discord.Embed(title = "Logging out", description = f"{emoji.wave_animated} See you soon!"))
        channel = self.bot.get_channel(vars.statusChannel)
        await channel.send(embed = embs.Offline)
        await self.bot.close()

    @botCommands.command(description = "Repeats what the user requests it to")
    @commands.is_owner()
    async def echo(self, ctx):
        await ctx.send_modal(EchoModal(title = "Echo"))

    cog_list = []

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_list.append(
                discord.OptionChoice(name = filename.split('.py')[0])
            )

    available_cog_options = discord.Option(str, description = "The cog to load/unload", choices = cog_list)

    cog_choices = [
        discord.OptionChoice(name = "Load"),
        discord.OptionChoice(name = "Unload"),
        discord.OptionChoice(name = "Reload")
    ]

    cog_options = discord.Option(str, description = "Whether to load, unload, or reload the cog", choices = cog_choices)

    @botCommands.command(description = "Load, unload, or reload the specified cog")
    @commands.is_owner()
    async def cog(self, ctx, operation: cog_options, extension: available_cog_options):
        try:
            if operation == "Load":
                self.bot.load_extension(f'cogs.{extension}')
            elif operation == "Unload":
                self.bot.unload_extension(f'cogs.{extension}')
            elif operation == "Reload":
                self.bot.reload_extension(f'cogs.{extension}')

            await ctx.respond(embed = embs.Success(f"Successfully {operation.lower()}ed `{extension}`"))
        except Exception as e:
            await ctx.respond(embed = embs.Failure(f"Couldn't {operation.lower()} {extension}", e))

def setup(bot):
    bot.add_cog(Owner(bot))