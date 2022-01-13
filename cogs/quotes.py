import discord, json, random
from discord.ext import commands
from discord_slash import cog_ext
from modules.embedvars import setembedvar, requestedbyfooter

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

# Slash command choices and options

addquote_options = [{"name":"messageid","description":"The message ID of the message you want to add as a quote.","type":3,"required":"true"}]
removequote_options = [{"name":"user","description":"The user the quote is attributed to.","type":6,"required":"true"},{"name":"messageid","description":"The message ID of the quote you want to remove.","type":3,"required":"true"}]

# Command functions

async def addquote(self, ctx, messageid):

    messageid = int(messageid)

    found = False

    for channel in ctx.guild.text_channels:

        try:
            message = await channel.fetch_message(messageid)
            found = True
            break
        except:
            found = False
    
    if found == False:

        await ctx.send(embed = setembedvar("R","Message Not Found",f"Couldn't find message with ID {messageid}."))
    
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

            if userQuotes[quote]["message_id"] == messageid:

                exists = True
                break
        
        if exists == True:

            existsEmbed = setembedvar("R", "Quote already added", f"The [requested quote]({quote['jump_url']}) already exists.")
            existsEmbed = requestedbyfooter(existsEmbed,ctx.message)
            await ctx.send(embed = existsEmbed)
        
        else:

            userQuotes[str(len(userQuotes)+1)] = quote
            await updateQuotes(message.author.id, userQuotes)

async def removequote(self, ctx, member: discord.User, messageID: int):
    
    memberID = ctx.message.content.split("<@!")[1].split(">")[0]
    userQuotes = await getQuotes(memberID)

    found = False

    for quote in userQuotes:
        
        if userQuotes[quote]["message_id"] == messageID:

            found = True
            userQuotes.pop(quote)
            await updateQuotes(memberID, userQuotes)
            await ctx.send(embed = setembedvar("G", "Deleted quote", f"Deleted {member.mention}'s quote with message ID {messageID}."))
            break
    
    if found == False:

        await ctx.send(embed = setembedvar("R","Quote Not Found",f"Couldn't find {member.mention}'s quote with message ID {messageID}."))

async def quote(self, ctx, member: discord.User):

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

        quoteEmbed = setembedvar(0xb00b69, title = title, description = description, author = member.name, author_icon = member.avatar_url, author_url = quote["jump_url"])
        quoteEmbed.set_footer(text = f"Quote added by {added_by.name} · {quote['added_by_id']}")
        await ctx.send(embed = quoteEmbed)
    
    else:

        noQuotes = setembedvar("R", "No quotes found", f"Looks like {member.mention} doesn't have any quotes. Add some and try again!")
        noQuotes = requestedbyfooter(noQuotes,ctx.message)
        await ctx.send(embed = noQuotes)

class Quotes(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # Add quote

    @cog_ext.cog_subcommand(name="add", base="quote", description="Add a quote for a user.", options=addquote_options)
    async def slash_addquote(self, ctx, messageID: int):
        await addquote(self, ctx, messageID)

    @commands.command(name="addquote")
    async def regular_addquote(self, ctx, messageID: int):
        await addquote(self, ctx, messageID)

    # Remove quote

    @cog_ext.cog_subcommand(name="remove", base="quote", description="Remove a quote for a user.", options=removequote_options)
    async def slash_removequote(self, ctx, member: discord.User, messageid: int):
        await removequote(self, ctx, member, messageid)
    
    @commands.command(name="removequote")
    async def regular_removequote(self, ctx, member: discord.User, messageid: int):
        await removequote(self, ctx, member, messageid)

    # Display quote

    @cog_ext.cog_subcommand(name="", base="quote", description="Display a random added quote from a user.")
    async def slash_quote(self, ctx, member: discord.User):
        await quote(self, ctx, member)

    @commands.command(name="quote")
    async def regular_quote(self, ctx, member: discord.User):
        await quote(self, ctx, member)

def setup(bot:commands.Bot):
    bot.add_cog(Quotes(bot))