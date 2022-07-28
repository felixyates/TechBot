import discord
from discord.ext import commands
from discord.commands import SlashCommand, SlashCommandGroup, ApplicationContext
from modules import embs, srv
from cogs import music

async def set_module_channel(ctx, module_name: str, channel: discord.TextChannel):
    module: srv.Server.Module = await srv.Server(ctx.guild.id).GetModule(module_name)
    callback = await module.SetChannel(channel)
    if callback["successful"]:
        await ctx.respond(embed = embs.Success(f"Channel set to {channel.mention}"))
    else:
        await ctx.respond(embed = callback["embed"])

async def set_module_status(ctx, module_name: str, state: int):
    server = srv.Server(ctx.guild.id)
    module: srv.Server.Module = await server.GetModule(module_name)

    if state == 1:
        if hasattr(module, "channel") and module.channel is not None:
                callback = await module.Enable()
                embed = callback["embed"]
        else:
            embed = embs.Failure("Set up the module first")
    else:
        callback = await module.Disable()
        embed = callback["embed"]

    await ctx.respond(embed = embed)

class WelcomeModal(discord.ui.Modal):
    def __init__(self, title, *args, **kwargs) -> None:
        super().__init__(title, *args)
        self.channel = kwargs.get("channel")
        self.add_item(discord.ui.InputText(
            label = "Message to send when a member joins",
            placeholder = "You can use the placeholders {member} and {servername} in your message",
            style = discord.InputTextStyle.long
        )
    )

    async def callback(self, interaction: discord.Interaction):
        shouldSet = False
        while not shouldSet:
            message = self.children[0].value
            tempMessage = message.replace("{member}", interaction.user.mention)
            tempMessage = message.replace("{servername}", interaction.guild.name)
            view = WelcomeView()
            await interaction.response.send_message(
                f"""This is what the welcome message will look like:
                {tempMessage}""",
                view = view
            )

class WelcomeView(discord.ui.View):
    def __init__(self, **kwargs):
        self.channel = kwargs.get("channel")

    @discord.ui.button(label = 'Confirm and enable', style = discord.ButtonStyle.success)
    async def confirm_callback(self, interaction, button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label = 'Reconfigure', style = discord.ButtonStyle.danger)
    async def reconfigure_callback(self, interaction, button):
        button.disabled = True
        modal = WelcomeModal(title = "Welcome message setup", channel = self.channel)
        await interaction.response.send_modal(modal)

# Slash command choices and options
state_choices = [discord.OptionChoice(name = 'On', value = 1), discord.OptionChoice(name = 'Off', value = 0)]
state_options = discord.Option(int, description = "Whether the module is on or off", choices = state_choices)
channel_options = discord.Option(discord.TextChannel, description = "The channel for the module to be active in")

class Administration(commands.Cog, name = 'administration'):
    def __init__(self, bot):
        self.bot = bot
    
    modules = SlashCommandGroup(
        name = 'module',
        description = "Commands to control the bot's modules in the server"
    )

    music = modules.create_subgroup(
        name = "music",
        description = "Commands related to the music module"
    )

    @music.command(name = "status", description = "Turns the music module on/off")
    @discord.default_permissions(administrator = True)
    async def music_status(self, ctx, state: state_options):
        await set_module_status(ctx, module_name = "music", state=state)
        await music.updateCache(self, ctx.guild.id)

    @music.command(name="channel", description="Sets the server's music channel")
    @discord.default_permissions(administrator = True)
    async def music_channel(self, ctx, channel: channel_options):
        await set_module_channel(ctx, module_name="music", channel=channel)

    welcome = modules.create_subgroup(
        name = "welcome",
        description = "Commands related to the welcome module"
    )

    @welcome.command(name="setup", description="Sets up the server's welcome module")
    @discord.default_permissions(administrator = True)
    async def welcome_setup(self, ctx,
        channel: discord.Option(discord.TextChannel, "The channel to send the welcome message in")
    ):
        modal = WelcomeModal(title = "Welcome message setup", channel = channel)
        await ctx.send_modal(modal)

    @welcome.command(name="status", description="Turns the welcome message on/off")
    @discord.default_permissions(administrator = True)
    async def welcome_status(self, ctx: ApplicationContext, state: state_options):
        await set_module_status(ctx, "welcome", state)

    slur_detector = modules.create_subgroup(
        name = "slurdetector",
        description = "Commands related to the slur detector module",
    )

    @slur_detector.command(name="status", description="Turns the slur detector on/off")
    @discord.default_permissions(administrator = True)
    async def slurdetector_status(self, ctx: ApplicationContext, state: state_options):
        await set_module_status(ctx, "slurdetector", state)

    @slur_detector.command(name="setup", description="Sets the slur detector moderation channel")
    @discord.default_permissions(administrator = True)
    async def slurdetector_setup(self, ctx: ApplicationContext, channel: channel_options):
        """Allows guild admins to use the slur detector module in their own server."""
        await set_module_channel(ctx, channel)
    
    textresponder_choices = [discord.OptionChoice("Enabled", 1), discord.OptionChoice("Disabled", 0)]

    text_responder = modules.create_subgroup(
        name = "textresponder",
        description = "Commands related to the text responder module"
    )

    @text_responder.command(name="state", base="textresponder", description="Turn text responder module on/off")
    @discord.default_permissions(administrator = True)
    async def textresponder(self, ctx,
        state: state_options
    ):        
        module = await srv.Server(ctx.guild.id).Module().Get('textresponder')

        if state == 1:
            callback = await module.Enable()
        elif state == 0:
            callback = await module.Disable()
        await ctx.respond(embed = callback["embed"])

def setup(bot):
    bot.add_cog(Administration(bot))