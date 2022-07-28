import discord, datetime
import discord.ext
from discord.ext import commands
from discord.ext.commands import \
    CommandNotFound, MissingRequiredArgument
from modules import srv, db, vars, embs, emoji
import cogs.music as music
from cogs.owner import Owner

class Listeners(commands.Cog, name = 'listeners'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await srv.Server(guild).Create(1)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await srv.Server(guild).Delete(2)

    @commands.Cog.listener()
    async def on_member_join(self,member):
        welcome: srv.Server.Module = await srv.Server(member.guild.id).GetModule('welcome')
        if welcome.IsEnabled():
            welcomeChannel = self.bot.get_channel(int(welcome.channel))
            welcomeMessage = welcome.message.replace("{member}",member.mention).replace("{servername}",member.guild.name)
            await welcomeChannel.send(welcomeMessage)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name} / {self.bot.user.id}"+"\n------")
        channel = self.bot.get_channel(vars.STATUSCHANNEL)
        await channel.send(embed = embs.Online())
        await music.updateCache.start(self.bot)
        await Owner.status_update.start(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot == False:
            if isinstance(message.channel, discord.channel.DMChannel):
                directMessageChannel = self.bot.get_channel(vars.dmChannel)
                dmEmbed = embs.Embed(description = message.content)
                dmEmbed.TimestampFooter()
                dmEmbed.set_author(name = message.author.mention, icon_url = message.author.avatar_url)
                dmEmbed.set_footer(text = f"User ID: {message.author.id}")
                await directMessageChannel.send(embed = dmEmbed)

                if message.attachments:
                    for attachment in message.attachments:
                        attachmentEmbed.set_image(attachment.url)
                        attachmentEmbed = embs.Embed(description = f"Attachment {attachment} of {len(message.attachments)} in message {message.id}")
                        attachmentEmbed.TimestampFooter()
                        attachmentEmbed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
                        attachmentEmbed.set_footer(text = f"User ID: {message.author.id}")
                        await directMessageChannel.send(embed = attachmentEmbed)

    @commands.Cog.listener() # slash command error handler
    async def on_application_command_error(self, ctx, ex):
        if isinstance(ex, discord.ext.commands.errors.MissingPermissions):
            await ctx.respond(embed = embs.Failure(ex))
        elif isinstance(ex, commands.NotOwner):
            await ctx.respond(embed = embs.Failure("Hey! This command is for bot owners only."))
        elif isinstance(ex, MissingRequiredArgument):
            await ctx.respond(embed= embs.Failure(f"Command Missing Argument(s): `{ex}`"))
        elif isinstance(ex, CommandNotFound):
            return
        else:
            channel = self.bot.get_channel(vars.errorChannel)
            if isinstance(ctx.channel, discord.channel.DMChannel):
                guildName = "Private DM"
                guildID = "N/A"
            else:
                guildName = ctx.guild.name
                guildID = ctx.guild.id

            embed = embs.Failure("An error occurred", ex)
            fields = [
                ["Command Issuer", f"{ctx.author.mention}"],
                ["Command", f"`{ctx.command}`"],
                ["Guild", f"{guildName} ({guildID})"],
                ["Channel", f"{ctx.channel.mention}"]
            ]
            embed.AddFields(fields)

            public_embed = embs.Failure("An error occurred", ex)
            public_embed.set_footer(text = f"Error triggered by {ctx.author.name} // {ctx.author.id}", icon_url = ctx.author.avatar.url)

            await ctx.respond(embed=public_embed)
            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Listeners(bot))