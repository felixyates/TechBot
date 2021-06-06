import discord, json, random
from discord.ext import commands
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


class Quotes(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot


    @commands.command()
    async def addquote(self, ctx, messageID: int):

        found = False

        for channel in ctx.guild.text_channels:

            try:
                message = await channel.fetch_message(messageID)
                found = True
                break
            except:
                found = False
        
        if found == False:

            await ctx.send(embed = setembedvar("R","Message Not Found",f"Couldn't find message with ID {messageID}."))
        
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

                print(quote)

                if userQuotes[quote]["message_id"] == messageID:

                    exists = True
                    break
            
            if exists == True:

                existsEmbed = setembedvar("R", "Quote already added", f"The [requested quote]({quote['jump_url']}) already exists.")
                existsEmbed = requestedbyfooter(existsEmbed,ctx.message)
                await ctx.send(embed = existsEmbed)
            
            else:

                userQuotes[str(len(userQuotes)+1)] = quote
                await updateQuotes(message.author.id, userQuotes)

    @commands.command()
    async def quote(self, ctx, member: discord.User):

        memberID = ctx.message.content.split("<@!")[1].split(">")[0]

        member = await self.bot.fetch_user(memberID)
        userQuotes = await getQuotes(memberID)

        if len(userQuotes) > 0:

            randomInt = str(random.randint(1, len(userQuotes)))
            print(userQuotes)
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
        

    @commands.command()
    async def delquote(self, ctx, member: discord.User, messageID: int):
        
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





def setup(bot:commands.Bot):
    bot.add_cog(Quotes(bot))