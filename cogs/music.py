import discord
from discord.ext import commands
from discord.ext.tasks import loop
from discord.commands import slash_command
from modules import emoji, srv, embs
from modules.music import spotify, youtube

global servers
servers = {}

@loop(seconds = 60)
async def updateCache(bot: discord.Bot, guild_id = None):
    if guild_id is None:
        global servers
        servers = {}
        async for guild in bot.fetch_guilds():
            servers[str(guild.id)] = await srv.Server(guild.id).GetModule('music')
    else:
        servers[str(guild_id)] = await srv.Server(guild_id).GetModule('music')

class Music(commands.Cog, name = 'music'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        error = botMsg = obj = None
        author, content = message.author, message.content

        if author.bot == False and message.guild != None:
            await updateCache(self, message.guild.id)
            music = servers[str(message.guild.id)]

            if (message.channel.id == int(music.channel_id)) and (music.state == 1):
                if content.startswith(spotify.URL1) or content.startswith(spotify.URL2):
                    source = "open.spotify.com/"
                    types = ["playlist","track","artist","album","user"]
                    id = None
                    for type in types:
                        removed = content.strip('/')
                        if f"{source}{type}" in removed:
                            id = await spotify.Funcs.idGetter(content, type)
                            type = type
                            break
                    
                    if id is not None:
                        if type == "playlist":
                            obj = spotify.Spotify.Playlist(id)
                        elif type == "track":
                            obj = spotify.Spotify.Track(id)
                        elif type == "artist":
                            obj = spotify.Spotify.Artist(id)
                        elif type == "album":
                            obj = spotify.Spotify.Album(id)
                        elif type == "user":
                            obj = spotify.Spotify.User(id)

                        botMsg = await message.channel.send(embed = await obj.GetEmbed(author))

                elif "youtube.com" in content:
                    try:
                        obj = youtube.Object(content)
                        obj = await obj.Get()
                    except youtube.findError as ex:
                        error = True
                        embed = embs.Failure(f"Error getting item details - it is private or was not found.", ex)
                        embed.set_footer(text=f"Failed recommendation by {message.author.display_name}",icon_url=message.author.avatar.url)
                        await message.channel.send(embed=embed, delete_after=7.5)

                    if obj != None and hasattr(obj, "GetEmbed"):
                            embed = await obj.GetEmbed(message.author)

                    if error != True:
                        botMsg = await message.channel.send(embed=embed)
                    else:
                        botMsg = None

                if botMsg != None:
                    await message.delete()
                    await botMsg.add_reaction(emoji.upvote)
                    await botMsg.add_reaction(emoji.downvote)

    @slash_command(name="songinfo", description="Gives info about a Spotify song")
    async def slash_songinfo(self, ctx,
        url: discord.Option(str, "The Spotify URL of the song")
    ):
        if url.startswith(spotify.URL1) == True or url.startswith(spotify.URL2) == True:
            id = url.replace(f"{spotify.URL1}track/","").replace(f"{spotify.URL2}track/","").split("?")[0]
            embed = await spotify.Track(id).GetEmbed(ctx.author)
            await ctx.respond(embed = embed)
        else:
            await ctx.respond(embed = embs.Failure("Invalid Spotify URL. Please make sure it is exactly as you copied it."))

def setup(bot):
    bot.add_cog(Music(bot))