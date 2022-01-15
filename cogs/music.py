import discord
import modules.music.spotify as spotify
import modules.music.youtube as youtube
from modules.music.youtube import findError
from discord.ext import commands
from modules.embedvars import setembedvar
from modules.emoji import upvote,downvote, nope
from modules.getjson import loadServerJson
from discord_slash import cog_ext

# Slash command options
songinfo_options = [{"name":"url","description":"The Spotify URL of the song.","type":3,"required":"true"}]

class Music(commands.Cog, name="music"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):

        error = False
        botMsg = None
        author, content= message.author, message.content

        if author.bot == False and message.guild != None:

            servers = loadServerJson()
            music = servers[str(message.guild.id)]["music"]
            enabled, channel = music["enabled"], music["channel"]

            if (message.channel.id == int(channel)) and (enabled == 1):
                if content.startswith(spotify.URL1) or content.startswith(spotify.URL2):
                    source = "open.spotify.com/"
                    types = ["playlist","track","artist","album","user"]

                    for type in types:
                        if f"{source}{type}/" in content:
                            id = await spotify.Funcs.idGetter(content, type)
                            type = type
                            break
                    
                    if type == "playlist":
                        obj = spotify.Playlist(id)
                    elif type == "track":
                        obj = spotify.Track(id)
                    elif type == "artist":
                        obj = spotify.Artist(id)
                    elif type == "album":
                        obj = spotify.Album(id)
                    elif type == "user":
                        obj = spotify.User(id)

                    botMsg = await message.channel.send(embed = await obj.getEmbed(author))

                elif content.startswith(youtube.URL1) or content.startswith(youtube.URL2):
                    source = "youtube.com/"
                    try:
                        if f"{source}playlist?list=" in content:
                            type = "playlist"
                            playlist_id = content.replace(f"{youtube.URL1}playlist?list=","").replace(f"{youtube.URL2}playlist?list=","")
                            obj = youtube.Playlist(playlist_id)
                        elif f"{source}watch?v=" in content:
                            type = "video"
                            video_id = (content.split("&")[0]).split("watch?v=")[1]
                            obj = youtube.Video(video_id)
                        elif f"{source}channel/" in content:
                            type = "channel"
                            channel_id = content.split("channel/")[1]
                            obj = youtube.Channel(channel_id)
                        else:
                            obj = None

                        if obj != None:
                            embed = await obj.getEmbed(message.author)

                    except findError:
                        error = True
                        embed = setembedvar("R",f"Error getting {type} details",f"Recommended {type} is private or was not found.")
                        embed.set_footer(text=f"Failed recommendation by {message.author.display_name}",icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed, delete_after=7.5)

                    if error == False:
                        botMsg = await message.channel.send(embed=embed)
                    else:
                        botMsg = None

                if botMsg != None:
                    await message.delete()
                    await botMsg.add_reaction(upvote)
                    await botMsg.add_reaction(downvote)

    @cog_ext.cog_slash(name="songinfo", description="Gives info about a Spotify song.", options=songinfo_options)
    async def slash_songinfo(self, ctx, url):
        if url.startswith(spotify.URL1) == True or url.startswith(spotify.URL2) == True:
            id = url.replace(f"{spotify.URL1}track/","").replace(f"{spotify.URL2}track/","").split("?")[0]
            embed = await spotify.Track(id).getEmbed(ctx.author)
            await ctx.send(embed = embed)
        else:
            print("Failed.")
            await ctx.send(f"{nope} Invalid Spotify URL. Please make sure it is exactly as you copied it.")

def setup(bot):
    bot.add_cog(Music(bot))