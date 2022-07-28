import discord, aiosqlite
from discord.ext import commands
from discord.commands import SlashCommandGroup
from modules import embs, db, srv, vars
from modules.classes import Responder
from cogs.administration import Administration

class ResponderModal(discord.ui.Modal):
    def __init__(self, title, *args, **kwargs) -> None:
        super().__init__(title, *args)

        self.responder_type = kwargs["responder_type"]
        self.add_item(discord.ui.InputText(label="Trigger", placeholder = "What you want to trigger the response"))
        self.add_item(discord.ui.InputText(label="Response", placeholder = "What you want the bot to send when triggered", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        trigger = self.children[0].value
        response = self.children[1].value
        responder = Responder(str(interaction.guild.id), trigger, type = self.responder_type, response = response, added_by = str(interaction.user.id))
        if (await responder.DoesExist() != None):
            await interaction.response.send_message(embed = embs.Failure(f"Responder already exists. Remove it using `/textresponder remove {trigger}` to add it again."))
        else:
            await db.AddResponder(str(interaction.guild.id), str(interaction.user.id), self.responder_type, trigger, response)
            await interaction.response.send_message(embed = embs.Success("Added responder"))

async def listResponders(ctx):
    "Prints the server's text responders."
    server = srv.Server(ctx.guild)
    embed = discord.Embed(f"Text Responders for {server.name}")
    embed = embs.RequestedByFooter(embed, ctx.author)
    embed.add_field(name = "Format", value = "Type | Trigger | Response | Added By", inline = False)
    responders = await getResponders(ctx.guild.id)

    for responder in responders:
        embed.add_field(
            name = responder.trigger,
            value=f'{responder.type} | {responder.trigger} | {responder.response} | {responder.added_by}', inline=False)

    return embed

async def getResponders(guild_id):
    "Fetches a server's responders"
    guild_id = str(guild_id)
    async with aiosqlite.connect(vars.dbPath) as db:
        async with db.execute(f"SELECT * FROM textresponder_triggers WHERE guild_id = ?", (guild_id,)) as cursor:
            temp_responders = await cursor.fetchall()
            responders = []
            for row in temp_responders:
                responder = Responder(
                    guild_id,
                    row[3],
                    type = row[2],
                    response = row[4],
                    added_by = f"<@{row[1]}>"
                )
                responders.append(responder)
            return responders
    
addresponder_choices = [discord.OptionChoice("Exact Match", 1), discord.OptionChoice("Contains", 2), discord.OptionChoice("Exact (Case Insensitive)", 3), discord.OptionChoice("Contains (Case Insensitive)", 4)]

class TextResponder(commands.Cog, name = 'textresponder'):
    """Allows for the creation, deletion, and handling of text responders.
    Members must have the `Manage Emojis` permission to create or delete responders.
    No special permissions are required for listing the server's text responders."""

    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Checks sent messages. If the message is one of the triggers in the database, it will send the specified response. If guild trigger matches, bot will send response.
        * Type 1 - exact match
        * Type 2 - contains
        * Type 3 - exact (case insensitive)
        * Type 4 - contains (case insensitive)"""

        module: srv.Server.Module = await srv.Server(message.guild.id).GetModule('textresponder')
        if module.IsEnabled() and message.author.bot == False:
            responders = await getResponders(str(message.guild.id))
            for responder in responders:
                responder: Responder
                if (await responder.ShouldSend(message.content)):
                    await message.channel.send(responder.response)
                    break

    @Administration.text_responder.command(name="add", description="Adds the requested text responder for the server.", default_member_permissions = discord.Permissions(manage_emojis=True))
    async def addresponder(self, ctx,
        type: discord.Option(int, "Type of text responder to add", choices = addresponder_choices),
    ):
        modal = ResponderModal(title = "Add text responder", responder_type = type)
        await ctx.send_modal(modal)

    @Administration.text_responder.command(name="remove", description="Removes all responders with the given trigger", default_member_permissions = discord.Permissions(manage_emojis=True))
    async def removeresponder(self, ctx,
        trigger: discord.Option(str, "The trigger of the responder you want to remove")
    ):
        responder = Responder(str(ctx.guild.id), trigger)
        removed = await responder.Remove()
        if (removed):
            await ctx.respond(embed = embs.Success("Removed responder"))
        else:
            await ctx.respond(embed = [embs.Failure(f"Couldn't remove responder: {removed}. You must enter a responder from the list below:"), await listResponders(ctx)])

    @Administration.text_responder.command(name="list", base="textresponder", description="Retrieves and shows the server's text responders.")
    async def responders(self,ctx):
        await ctx.respond(embed = await listResponders(ctx))
        
def setup(bot):
    bot.add_cog(TextResponder(bot))