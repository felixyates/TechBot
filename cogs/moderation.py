import discord, datetime, asyncio
from discord.ext import commands
from discord.ext.commands import \
    has_permissions, slash_command
from modules import emoji, embs

class Moderation(commands.Cog, name = 'moderation'):

    def __init__(self, bot):
        self.bot = bot

    messages = discord.SlashCommandGroup(
        name = 'messages',
        description = "Commands to help manage the server's messages",
    )

    @messages.command(name="delete", description="Deletes the specified number of messages (up to 14 days old)")
    @discord.default_permissions(manage_messages = True)
    async def delete(self, ctx,
        deletenumber: discord.Option(int, name = "messages", description = "Number of messages to delete", min_value = 1, max_value = 100)
    ):
        await ctx.respond("Working on it...")
        await ctx.defer()
        daysago = datetime.datetime.now() - datetime.timedelta(days=14)
        await ctx.message.delete()
        messages = await ctx.channel.history(limit = deletenumber, after = daysago).flatten()
        if len(messages) > 0:
            await ctx.channel.delete_messages(messages)
            await ctx.send(embed = embs.Success(f"Deleted {len(messages)} messages."))
        else:
            await ctx.respond(embed = embs.Failure("Messages either not found or sent more than 14 days ago."))

    @messages.command(name="purge", description="Deletes 100 messages under 14 days old")
    @discord.default_permissions(manage_messages = True)
    async def purge(self, ctx):
        await ctx.send("Working on it...")
        daysago = datetime.datetime.now() - datetime.timedelta(days=14)
        await ctx.defer()
        messages = await ctx.channel.history(limit=100, after=daysago).flatten()
        await ctx.channel.delete_messages(messages)
        await ctx.respond(embed = embs.Success(f"Deleted {len(messages)} messages."))

    class View(discord.ui.View):
        def __init__(self, messages):
            self.messages = messages
            super().__init__()

        @discord.ui.button(label = 'Confirm', style = discord.ButtonStyle.green)
        async def confirm_callback(self, button, interaction: discord.Interaction):
            messages = self.messages
            button.disabled = True
            try:
                channel: discord.TextChannel = await interaction.bot.fetch_channel(interaction.channel_id)
                messagesList = await channel.history(limit = self.messages).flatten()
                for message in messagesList:
                    for i in range(0, self.messages):
                        await message.delete()
                        if i%10 == 0:
                            await interaction.response.edit_message(embed = embs.Embed(f"{emoji.loading} Progress: {(i/messages)*100}% deleted ({i}/{messages})"))
                        if i == messages:
                            await interaction.response.edit_message(embed = embs.Success(f"Deleted {i} messages.", delete_after=5))
            except Exception as e:
                await interaction.response.edit_message(embed = embs.Failure("Couldn't delete messages. Try again or contact support.", e))


    @messages.command(name="slowdelete", description="Deletes specified number of messages (up to 1000). Not restricted by age of message")
    @discord.default_permissions(manage_messages = True)
    async def slowdelete(self, ctx: discord.ApplicationContext,
        messages: discord.Option(int, name = "messages", description = "Number of messages to delete", min_value = 1, max_value = 500)
    ):
            await ctx.respond(
                embed = embs.Embed(
                    title = "Are you sure?",
                    description = f"""Attempting to delete {messages} messages. This will take a long time, depending on how many messages you want to delete, and cannot be undone.
                    Are you sure you want to do this?"""
                ),
                view = Moderation.View(messages)
            )

def setup(bot):
    bot.add_cog(Moderation(bot))