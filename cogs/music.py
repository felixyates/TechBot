import discord, asyncio, spotipy, pyyoutube
from discord.ext import commands
from modules.embedvars import setembedvar
from modules.emoji import upvote,downvote,nope
from modules.getjson import secret, loadServerJson
from spotipy import SpotifyClientCredentials
from discord_slash import cog_ext

spotifyURL1 = "https://open.spotify.com/"
spotifyURL2 = "https://www.open.spotify.com/"
youtubeURL1 = "https://www.youtube.com/"
youtubeURL2 = "https://youtube.com/"
spDefaultPfp = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"
youtubeColour = 0xe62117
spotifyColour = 0x1db954

spotify = secret("spotify")
client_secret = spotify["private"]
client_id = spotify["public"]

yt_api_key = secret("youtube")

class findError(Exception):
    pass

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = spotify["public"], client_secret = spotify["private"]))
yt = pyyoutube.Api(api_key = yt_api_key)

# Slash command options

songinfo_options = [{"name":"url","description":"The Spotify URL of the song.","type":3,"required":"true"}]

# Classes, functions, etc.

class D2C(object):
    "Converts dictionary to class"
    def __init__(self, my_dict):
          
        for key in my_dict:
            setattr(self, key, my_dict[key])

class Spotify(object):

    class Funcs(object):

        async def idGetter(messageContent: str, contentType: str):

            id = messageContent.replace(f"{spotifyURL1}{contentType}/","")
            print(id)
            id = id.replace(f"{spotifyURL2}{contentType}/","")
            print(id)
            id = id.split("?")[0]
            return id
    
    class Embed(object):

        async def SetFooter(embed: discord.Embed, author: discord.User, type: str):

            embed.set_footer(text=f"{type} recommended by {author.display_name} • Data provided by Spotify.",icon_url=author.avatar_url)
            return embed

        async def Artist(id, author):

            artist = D2C(sp.artist(id))
            uri = artist.uri
            top_tracks = D2C(sp.artist_top_tracks(uri))

            try:
                
                artist_icon = artist.images[0]["url"]

            except:

                artist_icon = spDefaultPfp

            # Setting up embed

            if len(top_tracks.tracks) > 0:

                topTrack = D2C(top_tracks.tracks[0])
                trackName = topTrack.name
                trackURL = topTrack.external_urls["spotify"]
                album = topTrack.album
                albumName = album["name"]
                albumURL = album["external_urls"]["spotify"]
                album_icon = album["images"][0]["url"]
                embed = discord.Embed(title = trackName, url = trackURL, description = "Most popular song (USA)\n"+f"on [{albumName}]({albumURL})", color= spotifyColour)

            else:

                album_icon = ""
                embed= discord.Embed(title="", description="Artist does not have enough plays for top songs.", color= spotifyColour)

            embed.set_author(name = artist.name, url = artist.external_urls["spotify"], icon_url = artist_icon)
            embed.set_thumbnail(url = album_icon)
            embed.add_field(name="Followers", value= artist.followers['total'], inline=True)
            embed.add_field(name="Artist Popularity", value=f"{artist.popularity}%", inline=True)
            embed = await Spotify.Embed.SetFooter(embed, author, "Artist")
            return embed

        async def Playlist(id, author):

            playlist = D2C(sp.playlist(id))

            # Setting all variables using playlist object

            description = playlist.description

            try:
                imageurl = playlist.images[0]["url"]
            except:
                imageurl = ""

            # Cleaning up playlist description (Spotify handles characters weirdly).
                # Need to work on this - it doesn't work.
        
            replaceList = [['&amp;','&'],['&#x2F;','/']]

            if description.startswith('<a href='):
                description = ""
            else:
                description = description.split('<a href="')
                description = str(description[0])
                for i in range(len(replaceList)):
                    if replaceList[i][0] in description:
                        description.replace(replaceList[i][0], replaceList[i][1])
        
            # Getting playlist owner information.

            ownerID = str(playlist.owner["id"])

            # Using owner object to get playlist owner URL and icon.

            owner = D2C(sp.user(ownerID))
            owner_icon = owner.images
            try:
                owner_icon = owner_icon[(len(owner_icon)-1)]["url"]
            except:
                owner_icon = spDefaultPfp

            # Setting up embed

            embed=discord.Embed(title= playlist.name, url= playlist.external_urls["spotify"], description=description, color=spotifyColour)
            embed.set_author(name= playlist.owner["display_name"], url= owner.external_urls["spotify"], icon_url= owner_icon)
            embed.set_thumbnail(url= imageurl)
            embed.add_field(name="Tracks", value= playlist.tracks["total"], inline=True)
            embed.add_field(name="Followers", value= playlist.followers["total"], inline=True)
            embed = await Spotify.Embed.SetFooter(embed, author, "Playlist")
            return embed

        async def Album(id, author):

            album = D2C(sp.album(id))

            # Using album object to set variables.

            name = album.name
            url = album.external_urls["spotify"]
            release_date = album.release_date
            tracks = album.tracks["total"]
            icon = album.images[0]["url"]

            # Getting track list

            trackList = []

            for x in range(len(album.tracks["items"])):
                trackList.append(album.tracks["items"][x])
            
            # Formatting track list

            formattedTrackList = ""

            for i in range(len(trackList)):
                if i < 5:
                    formattedTrackList += f"{i+1}. [{trackList[i]['name']}]({trackList[i]['external_urls']['spotify']})" + "\n"

            if len(trackList) > 5:
                remainingTracks = tracks - 5
                formattedTrackList += f"+ {remainingTracks} more songs..."

            # Getting artist information.

            artists = album.artists
            artistsName = []

            
            mainArtist = album.artists[0]
            mainArtistID = mainArtist["id"]
            mainArtistName = mainArtist["name"]
            mainArtistURL = mainArtist["external_urls"]["spotify"]
            mainArtistObject = sp.artist(mainArtistID)
            

            for i in range(len(artists)):
                artistID = artists[i]["id"]
                artistObject = D2C(sp.artist(artistID))
                artistURL = artistObject.external_urls["spotify"]
                tempArtist = []
                tempArtist.append(artists[i]["name"])
                tempArtist.append(artistURL)
                artistsName.append(tempArtist)
            
            # Getting artist's icon from artist object

            try:
                mainArtist_icon = mainArtistObject["images"]
                mainArtist_icon = mainArtist_icon[(len(mainArtist_icon)-1)]["url"]
            except:
                mainArtist_icon = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"

            # Setting up embed

            embed = setembedvar(spotifyColour, name, url= url, author = mainArtistName, author_url = mainArtistURL, author_icon = mainArtist_icon, thumbnail = icon)
            embed.add_field(name="Release Date", value = release_date)
            embed.add_field(name="Tracks", value = tracks)
            embed.add_field(name="Track List", value = formattedTrackList, inline = False)
            embed = await Spotify.Embed.SetFooter(embed, author, "Album")

            # Handling multiple artists (if present).

            artistVar = ""

            if len(artists) > 1:
                for i in range(1,len(artistsName)):
                    artistVar = artistVar + "\n"+ f"[{artistsName[i][0]}]({artistsName[i][1]})"
                embed.add_field(name="Other Artists", value=artistVar)

            return embed

        async def User(id, author):
            
            user = D2C(sp.user(id))

            display_name = user.display_name
            url = user.external_urls["spotify"]
            followers = user.followers["total"]

            try:
                pfp = user.images[0]["url"]
            except:
                pfp = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"

            playlists = sp.user_playlists(id, limit=5)

            playlistStr = ""
            pos = 0
            items = playlists["items"]
            has_playlists = False

            if len(items) > 0:

                has_playlists = True

                for x in items:

                    pos += 1
                    playlistStr = playlistStr + f"{pos}. [{x['name']}]({x['external_urls']['spotify']})" + "\n"

                remaining = playlists['total'] - pos

                if remaining > 0:

                    playlistStr = playlistStr + f"+ {remaining} more"

                firstPlaylistThumbnail = playlists["items"][0]["images"][0]["url"]
            
            if has_playlists == True:

                embed = setembedvar(spotifyColour, title="", author=display_name, author_url=url, author_icon=pfp, thumbnail = firstPlaylistThumbnail)
                embed.add_field(name = "Followers", value = followers)
                embed.add_field(name = "Public Playlists", value = playlistStr, inline=False)
            
            else:

                embed = setembedvar(spotifyColour, title="", author=display_name, author_url=url, author_icon=pfp)
                embed.add_field(name = "Followers", value = followers)
                embed.add_field(name = "No Public Playlists", value="Make sure they're public.", inline=False)

            embed = await Spotify.Embed.SetFooter(embed, author, "User")
            return embed

        async def Track(id, author):
            
            track = sp.track(id)

            # Using track object to set variables.

            name = track["name"]
            url = track["external_urls"]["spotify"]
            preview_url = track["preview_url"]

            # Calculating track length and formatting it appropriately.

            durationSecs = (track["duration_ms"]/1000)
            durationMins = durationSecs // 60
            remainderSecs = round(durationSecs - (durationMins*60))

            if remainderSecs < 10:
                remainderSecs = f"0{remainderSecs}"

            duration = f"{int(durationMins)}:{remainderSecs}"

            # Getting artist information.

            artists = track["artists"]
            artistsName = []


            mainArtist = track["artists"][0]
            mainArtistID = mainArtist["id"]
            mainArtistName = mainArtist["name"]
            mainArtistURL = mainArtist["external_urls"]["spotify"]
            mainArtistObject = sp.artist(mainArtistID)
            

            for i in range(len(artists)):
                artistID = artists[i]["id"]
                artistObject = sp.artist(artistID)
                artistURL = artistObject["external_urls"]["spotify"]
                tempArtist = []
                tempArtist.append(artists[i]["name"])
                tempArtist.append(artistURL)
                artistsName.append(tempArtist)
            
            # Getting artist's icon from artist object
            
            try:
                mainArtist_icon = mainArtistObject["images"]
                mainArtist_icon = mainArtist_icon[(len(mainArtist_icon)-1)]["url"]
            except:
                mainArtist_icon = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"

            # Getting album information and cover image.

            album = track["album"]
            album_name = album["name"]
            album_image = album["images"]
            album_image = album_image[(len(album_image)-1)]["url"]

            # Setting up embed.
            
            embed = setembedvar(spotifyColour, name, url=url, author=mainArtistName, author_url=mainArtistURL, author_icon=mainArtist_icon, thumbnail=album_image)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Album", value=f"[{album_name}](https://open.spotify.com/album/{album['uri'].strip('spotify:album:')}/)", inline=True)

            if preview_url is not None:
                embed.add_field(name="Preview", value=f"[Download]({preview_url})", inline=True)

            # Handling multiple artists (if present).

            artistVar = ""

            if len(artists) > 1:
                for i in range(1,len(artistsName)):
                    artistVar = artistVar + "\n"+ f"[{artistsName[i][0]}]({artistsName[i][1]})"
                embed.add_field(name="Other Artists", value=artistVar)
            
            embed = await Spotify.Embed.SetFooter(embed, author, "Track")
            return embed

class YouTube(object):

    async def VideoEmbed(video_id,message):

        video = yt.get_video_by_id(video_id = video_id).to_dict()
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        if len(video["items"]) != 0:

            snippet = video["items"][0]["snippet"]
            title = snippet["title"]
            thumbnail = snippet["thumbnails"]["default"]["url"]
            duration = video["items"][0]["contentDetails"]["duration"]

            PT = [["H","h "],["M","m "],["S","s"]]

            if duration.startswith("PT") == True:
                duration = duration.strip("PT")
                for i in PT:
                    duration = duration.replace(i[0],i[1])
            else:
                duration = duration.strip("P")
                duration = duration.replace("DT","")
                days = duration[0]
                duration = duration[1:]
                for i in PT:
                    duration = duration.replace(i[0],i[1])
                duration = f"{days}d {duration}"

            channelID = snippet["channelId"]
            channelTitle = snippet["channelTitle"]

            channel = yt.get_channel_info(channel_id = channelID).to_dict()

            channelIcon = channel["items"][0]["snippet"]["thumbnails"]["default"]["url"]
            channelURL = f"https://www.youtube.com/channel/{channelID}"

            stats = video["items"][0]["statistics"]

            views = stats["viewCount"]
            likes = stats["likeCount"]
            dislikes = stats["dislikeCount"]

            embed=discord.Embed(title=title, url=video_url, color=youtubeColour)
            embed.set_author(name=channelTitle, url=channelURL, icon_url=channelIcon)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name="Views", value=views, inline=True)
            embed.add_field(name="Likes", value=likes, inline=True)
            embed.add_field(name="Dislikes", value=dislikes, inline=True)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.set_footer(text=f"Video recommended by {message.author.display_name}",icon_url=message.author.avatar_url)
        else:
            raise findError
        return embed

    async def PlaylistEmbed(playlist_id, message):

        playlist = yt.get_playlist_by_id(playlist_id = playlist_id).to_dict()
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

        if len(playlist["items"]) != 0:
            snippet = playlist["items"][0]["snippet"]
            title = snippet["title"]
            description = snippet["description"]
            thumbnail = snippet["thumbnails"]["default"]["url"]
            videos = playlist["items"][0]["contentDetails"]["itemCount"]

            channelID = snippet["channelId"]
            channelTitle = snippet["channelTitle"]

            channel = yt.get_channel_info(channel_id = channelID).to_dict()

            channelIcon = channel["items"][0]["snippet"]["thumbnails"]["default"]["url"]
            channelURL = f"https://www.youtube.com/channel/{channelID}"

            embed=discord.Embed(title=title, url=playlist_url, description=description, color=youtubeColour)
            embed.set_author(name=channelTitle, url=channelURL, icon_url=channelIcon)
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name="Videos", value=videos, inline=True)
            embed.set_footer(text=f"Playlist recommended by {message.author.display_name}",icon_url=message.author.avatar_url)
        else:
            raise findError
        return embed

    async def ChannelEmbed(channel_id, message):
    
        channel = yt.get_channel_info(channel_id = channel_id).to_dict()
        channel_url = f"https://www.youtube.com/channel/{channel_id}"

        if channel["pageInfo"]["totalResults"] > 0:
            snippet = channel["items"][0]["snippet"]
            statistics = channel["items"][0]["statistics"]
            title = snippet["title"]
            description = snippet["description"]
            subscribers = statistics["subscriberCount"]
            videos = statistics["videoCount"]
            views = statistics["viewCount"]
            channelIcon = channel["items"][0]["snippet"]["thumbnails"]["default"]["url"]

            embed=discord.Embed(description=description, color=youtubeColour)
            embed.set_author(name=title, url=channel_url, icon_url=channelIcon)
            embed.add_field(name="Subscribers", value=subscribers, inline=True)
            embed.add_field(name="Videos", value=videos, inline=True)
            embed.add_field(name="Total Views", value=views, inline=True)
            embed.set_footer(text=f"Channel recommended by {message.author.display_name}",icon_url=message.author.avatar_url)
            return embed
        else:
            raise findError

def durationFormatter(duration_ms):
    # Calculating track/video length and formatting it appropriately.

    durationSecs = (duration_ms/1000)
    durationMins = durationSecs // 60
    remainderSecs = round(durationSecs - (durationMins*60))

    if remainderSecs < 10:
        remainderSecs = f"0{remainderSecs}"

    if durationMins >= 60:
        durationHrs = durationMins // 60
        remainderMins = round(durationMins - (durationHrs*60))
        duration = f"{durationHrs}:{remainderMins}:{remainderSecs}"
    else:
        duration = f"{int(durationMins)}:{remainderSecs}"

    return duration

class Music(commands.Cog, name="music"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):

        error = False
        author = message.author
        content = message.content

        if author.bot == False and message.guild != None:

            servers = loadServerJson()
            music = servers[str(message.guild.id)]["music"]
            enabled = music["enabled"]
            channel = music["channel"]

            if (message.channel.id == int(channel)) and (enabled == 1):
            
                # Determines data source to pull info from

                if content.startswith(spotifyURL1) or content.startswith(spotifyURL2):
                    source = "open.spotify.com/"

                    types = ["playlist","track","artist","album","user"]

                    for type in types:

                        if f"{source}{type}/" in content:

                            id = await Spotify.Funcs.idGetter(content, type)
                            type = type
                            break
                    
                    if type == "playlist":

                        botMsg = await message.channel.send(embed= await Spotify.Embed.Playlist(id, author))

                    elif type == "track":

                        botMsg = await message.channel.send(embed = await Spotify.Embed.Track(id, author))

                    elif type == "artist":

                        botMsg = await message.channel.send(embed = await Spotify.Embed.Artist(id, author))

                    elif type == "album":

                        botMsg = await message.channel.send(embed = await Spotify.Embed.Album(id, author))
                    
                    elif type == "user":

                        botMsg = await message.channel.send(embed = await Spotify.Embed.User(id, author))

                elif content.startswith(youtubeURL1) or content.startswith(youtubeURL2):
                    source = "youtube.com/"

                    if f"{source}playlist?list=" in content:

                        playlist_id = content.replace("https://www.youtube.com/playlist?list=","")
                        video_id = content.replace("https://youtube.com/playlist?list=","")

                        try:

                            embed = await YouTube.PlaylistEmbed(playlist_id,message)

                        except findError:

                            error = True
                            errorType = "playlist"
                            error_url = f"https://www.youtube.com/playlist?list={playlist_id}"

                    elif f"{source}watch?v=" in content:

                        video_id = content.split("&")[0]
                        video_id = video_id.split("youtube.com/watch?v=")[1]

                        try:

                            embed = await YouTube.VideoEmbed(video_id,message)

                        except findError:

                            error = True
                            errorType = "video"
                            error_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    elif f"{source}channel/" in content:

                        channel_id = content.split("youtube.com/channel/")[1]
                        try:
                            embed = await YouTube.ChannelEmbed(channel_id, message)
                        except findError:
                            error = True
                            errorType = "channel"
                            error_url = f"https://www.youtube.com/channel/{channel_id}"

                    else:
                        source = "none"
                    
                    if error == True:

                        embed = setembedvar("R",f"Error getting {errorType} details",f"[Recommended {errorType}]({error_url}) is private or was not found.")
                        embed.set_footer(text=f"Failed recommendation by {message.author.display_name}",icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed, delete_after=7.5)

                    else:

                        botMsg = await message.channel.send(embed=embed)
            
                else:
                    source = None
                    
                    error = False
                    botMsg = None

                if source != None:

                    await message.delete()

                    if source != "unsupported" and botMsg != None:
                        await botMsg.add_reaction(upvote)
                        await botMsg.add_reaction(downvote)

    @cog_ext.cog_slash(name="songinfo", description="Gives info about a Spotify song.", options=songinfo_options)
    async def slash_songinfo(self, ctx, url):

        if url.startswith(spotifyURL1) == True or url.startswith(spotifyURL2) == True:

            id = url.replace(f"{spotifyURL1}track/","")
            id = id.replace(f"{spotifyURL2}track/","")
            id = id.split("?")[0]

            track = sp.track(id)
            tr_adv = sp.audio_features(id)[0]

            name = track["name"]
            url = track["external_urls"]["spotify"]
            preview_url = track["preview_url"]

            danceability = f'{round(tr_adv["danceability"]*100, 1)}%'
            energy = f'{round(tr_adv["energy"]*100, 1)}%'
            key = tr_adv["key"]
            tempo = round(tr_adv["tempo"], 1)

            # Calculating track length and formatting it appropriately.

            durationSecs = (track["duration_ms"]/1000)
            durationMins = durationSecs // 60
            remainderSecs = round(durationSecs - (durationMins*60))

            if remainderSecs < 10:
                remainderSecs = f"0{remainderSecs}"

            duration = f"{int(durationMins)}:{remainderSecs}"

            # Getting artist information.

            artists = track["artists"]
            artistsName = []


            mainArtist = track["artists"][0]
            mainArtistID = mainArtist["id"]
            mainArtistName = mainArtist["name"]
            mainArtistURL = mainArtist["external_urls"]["spotify"]
            mainArtistObject = sp.artist(mainArtistID)
            

            for i in range(len(artists)):
                artistID = artists[i]["id"]
                artistObject = sp.artist(artistID)
                artistURL = artistObject["external_urls"]["spotify"]
                tempArtist = []
                tempArtist.append(artists[i]["name"])
                tempArtist.append(artistURL)
                artistsName.append(tempArtist)
            
            # Getting artist's icon from artist object
            
            try:
                mainArtist_icon = mainArtistObject["images"]
                mainArtist_icon = mainArtist_icon[(len(mainArtist_icon)-1)]["url"]
            except:
                mainArtist_icon = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"

            # Getting album information and cover image.

            album = track["album"]
            album_name = album["name"]
            album_url = album["external_urls"]["spotify"]
            album_image = album["images"]
            album_image = album_image[0]["url"]

            embed = discord.Embed(title = name, url = url)
            embed.set_author(name = mainArtistName, url = mainArtistURL, icon_url = mainArtist_icon)
            embed.add_field(name = "Album", value = f"[{album_name}]({album_url})")
            embed.set_thumbnail(url=album_image)

            if preview_url != None:
                embed.add_field(name = "Preview", value = f"[Download]({preview_url})")

            embed.add_field(name = "Duration", value = duration)
            embed.add_field(name = "Danceability", value = danceability)
            embed.add_field(name = "Energy", value = energy)
            embed.add_field(name = "Key", value = key)
            embed.add_field(name = "Tempo", value = tempo)
            await ctx.send(embed = embed)

        else:

            print("Failed.")
            await ctx.send(f"{nope} Invalid Spotify URL. Please make sure it is exactly as you copied it.")


def setup(bot):
    bot.add_cog(Music(bot))