import discord, json, random
from discord.ext import commands
from discord.commands import SlashCommandGroup
from modules import embs

global getQuotes, updateQuotes

async def getQuotes(user):
    with open('quotes.json', 'r') as f:
        quotes = json.load(f)
        if str(user) in quotes:
            userQuotes = quotes[str(user)]
        else:
            userQuotes = {}
            await updateQuotes(user, {})
        return userQuotes

async def updateQuotes(userID, userQuotes):
    with open('quotes.json', 'r') as f:
        quotes = json.load(f)
    with open('quotes.json', 'w') as f:
        quotes[str(userID)] = userQuotes
        json.dump(quotes, f, indent=4)

class Quotes(commands.Cog, name = 'quotes'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    quote = SlashCommandGroup("quote", "Commands related to the quote module")

    @quote.command(name="add", base="quote", description="Add a quote for a member")
    async def slash_addquote(self, ctx,
        message_id: discord.Option(int, description="The message ID of the message you want to add as a quote")
    ):
        message_id = int(message_id)
        found = False
        for channel in ctx.guild.text_channels:
            try:
                message = await channel.fetch_message(message_id)
                found = True
                break
            except:
                found = False
        if found == False:
            await ctx.send(embed = embs.Failure(title = "Message Not Found", description = "Couldn't find message with ID {message_id}."))
        
        else:
            quote = {}
            quote["author_id"] = message.author.id
            quote["message_id"] = message.id
            quote["guild_id"] = ctx.guild.id
            quote["channel_id"] = message.channel.id
            quote["added_by_id"] = ctx.author.id
            quote["text"] = message.content
            quote["jump_url"] = message.jump_url
            
            userQuotes = await getQuotes(message.author.id)
            exists = False

            for quote in userQuotes:
                if userQuotes[quote]["message_id"] == message_id:
                    exists = True
                    break
            
            if exists == True:
                existsEmbed = embs.Failure(title = "Quote already added", description = f"The [requested quote]({quote['jump_url']}) already exists.")
                existsEmbed.RequestedByFooter(ctx.message.author)
                await ctx.send(embed = existsEmbed)
            
            else:
                userQuotes[str(len(userQuotes)+1)] = quote
                await updateQuotes(message.author.id, userQuotes)

    @quote.command(name="remove", base="quote", description="Remove a quote for a member")
    async def removequote(self, ctx,
        member: discord.Option(discord.User, description = "The member the quote is attributed to"),
        message_id: discord.Option(int, description = "The message ID of the quote you want to remove")
    ):
        memberID = ctx.message.content.split("<@!")[1].split(">")[0]
        userQuotes = await getQuotes(memberID)
        found = False

        for quote in userQuotes:
            if userQuotes[quote]["message_id"] == message_id:
                found = True
                userQuotes.pop(quote)
                await updateQuotes(memberID, userQuotes)
                await ctx.send(embed = embs.Success(f"Deleted {member.mention}'s quote with message ID {message_id}."))
                break
        
        if found == False:
            await ctx.send(embed = embs.Failure(f"Couldn't find {member.mention}'s quote with message ID {message_id}."))

    @quote.command(base="quote", description="Display a random added quote from a member")
    async def quote(self, ctx,
        member: discord.Option(discord.User, "The member you want to see a quote from")
    ):
        memberID = ctx.message.content.split("<@!")[1].split(">")[0]
        member = await self.bot.fetch_user(memberID)
        userQuotes = await getQuotes(memberID)

        if len(userQuotes) > 0:
            randomInt = str(random.randint(1, len(userQuotes)))
            quote = userQuotes[randomInt]
            added_by = await self.bot.fetch_user(quote["added_by_id"])
            if len(quote["text"]) > 256:
                title = f"Quote by {member.name}"
                description = quote["text"]
            
            else:
                title = quote["text"]
                description = ""

            quoteEmbed = embs.Embed(colour = 0xb00b69, title = title, description = description, author = member.name, author_icon = member.avatar.url, author_url = quote["jump_url"])
            quoteEmbed.set_footer(text = f"Quote added by {added_by.name} · {quote['added_by_id']}")
            await ctx.send(embed = quoteEmbed)
        
        else:
            noQuotes = embs.Failure(f"Looks like {member.mention} doesn't have any quotes. Add some and try again!")
            noQuotes.RequestedByFooter(ctx.message.author)
            await ctx.send(embed = noQuotes)

def setup(bot:commands.Bot):
    bot.add_cog(Quotes(bot))