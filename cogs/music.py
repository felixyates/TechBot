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
spotifyColour = 0x1db954
youtubeColour = 0xe62117

spotify = secret("spotify")
client_secret = spotify["private"]
client_id = spotify["public"]

yt_api_key = secret("youtube")

class findError(Exception):
    pass

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = spotify["public"], client_secret = spotify["private"]))
yt = pyyoutube.Api(api_key = yt_api_key)

class D2C(object):
    "Converts dictionary to class"
    def __init__(self, my_dict):
          
        for key in my_dict:
            setattr(self, key, my_dict[key])

class Spotify(object):

    async def idGetter(messageContent: str, contentType: str):

        id = messageContent.replace(f"{spotifyURL1}{contentType}/","")
        id = id.replace(f"{spotifyURL2}{contentType}/","")
        id = id.split("?")[0]
        return id

    async def ArtistEmbed(id, message):

        artist = D2C(sp.artist(id))
        uri = artist.uri
        top_tracks = D2C(sp.artist_top_tracks(uri))

        try:
            
            artist_icon = artist.images[0]["url"]

        except:

            artist_icon = spDefaultPfp

        # Using message.author for footer

        authorName = message.author.display_name
        authorAvatar = message.author.avatar_url

        # Setting up embed

        if len(top_tracks.tracks) > 0:

            topTrack = D2C(top_tracks.tracks[0])
            trackName = topTrack.name
            trackURL = topTrack.external_urls["spotify"]
            album = topTrack.album
            albumName = album["name"]
            albumURL = album["external_urls"]["spotify"]
            album_icon = album["images"][0]["url"]

            embed=discord.Embed(title = trackName, url = trackURL, description = "Most popular song (USA)\n"+f"From [{albumName}]({albumURL})", color=spotifyColour)

        else:

            album_icon = ""
            embed=discord.Embed(title="", description="Artist does not have enough plays for top songs.", color=spotifyColour)

        embed.set_author(name = artist.name, url = artist.external_urls["spotify"], icon_url = artist_icon)
        embed.set_thumbnail(url = album_icon)
        embed.add_field(name="Followers", value= artist.followers['total'], inline=True)
        embed.add_field(name="Artist Popularity", value=f"{artist.popularity}%", inline=True)
        embed.set_footer(text=f"Artist recommended by {authorName}",icon_url=authorAvatar)
        return embed

    async def PlaylistEmbed(id,message):

        playlist = D2C(sp.playlist(id))

        # Setting all variables using playlist object

        name = playlist.name
        url = playlist.external_urls["spotify"]
        trackTotal = playlist.tracks["total"]
        followers = playlist.followers["total"]
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

        owner = playlist.owner
        ownerID = str(owner["id"])
        ownerName = owner["display_name"]

        # Using owner object to get playlist owner URL and icon.

        owner = D2C(sp.user(ownerID))
        ownerURL = owner.external_urls["spotify"]
        owner_icon = owner.images
        try:
            owner_icon = owner_icon[(len(owner_icon)-1)]["url"]
        except:
            owner_icon = spDefaultPfp

        # Using message.author for footer

        authorName = message.author.display_name
        authorAvatar = message.author.avatar_url

        # Setting up embed

        embed=discord.Embed(title=name, url=url, description=description, color=spotifyColour)
        embed.set_author(name=ownerName, url=ownerURL, icon_url=owner_icon)
        embed.set_thumbnail(url=imageurl)
        embed.add_field(name="Tracks", value=trackTotal, inline=True)
        embed.add_field(name="Followers", value=followers, inline=True)
        embed.set_footer(text=f"Playlist recommended by {authorName}",icon_url=authorAvatar)

        return embed

    async def AlbumEmbed(id,message):

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

        # Using message.author for footer

        authorName = message.author.display_name
        authorAvatar = message.author.avatar_url

        # Setting up embed

        embed = setembedvar(spotifyColour, name, url= url, author = mainArtistName, author_url = mainArtistURL, author_icon = mainArtist_icon, thumbnail = icon)
        embed.add_field(name="Release Date", value = release_date)
        embed.add_field(name="Tracks", value = tracks)
        embed.add_field(name="Track List", value = formattedTrackList, inline = False)
        embed.set_footer(text=f"Album recommended by {authorName}", icon_url = authorAvatar)

        # Handling multiple artists (if present).

        artistVar = ""

        if len(artists) > 1:
            for i in range(1,len(artistsName)):
                artistVar = artistVar + "\n"+ f"[{artistsName[i][0]}]({artistsName[i][1]})"
            embed.add_field(name="Other Artists", value=artistVar)

        return embed

    async def UserEmbed(id,message):
        
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

        embed.set_footer(text = f"User recommended by {message.author.name}", icon_url = message.author.avatar_url)

        return embed

    async def TrackEmbed(id,message):
        
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

        # Using message.author for footer

        authorName = message.author.display_name
        authorAvatar = message.author.avatar_url

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
            embed.add_field(name="Preview", value=f"[Expires after 1 day]({preview_url})", inline=True)

        # Handling multiple artists (if present).

        artistVar = ""

        if len(artists) > 1:
            for i in range(1,len(artistsName)):
                artistVar = artistVar + "\n"+ f"[{artistsName[i][0]}]({artistsName[i][1]})"
            embed.add_field(name="Other Artists", value=artistVar)

        # Adding footer and returning embed.

        embed.set_footer(text=f"Song recommended by {authorName}",icon_url=authorAvatar)
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

            if duration.startswith("PT") == True:
                duration = duration.strip("PT")
                duration = duration.replace("H","h ")
                duration = duration.replace("M","m ")
                duration = duration.replace("S", "s")
            else:
                print(duration)
                duration = duration.strip("P")
                duration = duration.replace("DT","")
                days = duration[0]
                duration = duration[1:]
                duration = duration.replace("H","h ")
                duration = duration.replace("M","m ")
                duration = duration.replace("S","s")
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

        if message.author.bot == False and message.guild != None:

            servers = loadServerJson()
            music = servers[str(message.guild.id)]["music"]
            enabled = music["enabled"]
            channel = music["channel"]

            if (message.channel.id == int(channel)) and (enabled == 1):
            
                # Determines data source to pull info from

                if message.content.startswith(spotifyURL1) or message.content.startswith(spotifyURL2):
                    source = "open.spotify.com/"

                    if f"{source}playlist/" in message.content:

                        id = await Spotify.idGetter(message.content, "playlist")
                        botMsg = await message.channel.send(embed= await Spotify.PlaylistEmbed(id,message))

                    elif f"{source}track/" in message.content:

                        id = await Spotify.idGetter(message.content, "track")
                        botMsg = await message.channel.send(embed = await Spotify.TrackEmbed(id,message))

                    elif f"{source}artist/" in message.content:

                        id = await Spotify.idGetter(message.content, "artist")
                        botMsg = await message.channel.send(embed = await Spotify.ArtistEmbed(id,message))

                    elif f"{source}album/" in message.content:

                        id = await Spotify.idGetter(message.content, "album")
                        botMsg = await message.channel.send(embed = await Spotify.AlbumEmbed(id,message))
                    
                    elif f"{source}user/" in message.content:

                        id = await Spotify.idGetter(message.content, "user")
                        botMsg = await message.channel.send(embed = await Spotify.UserEmbed(id,message))

                elif message.content.startswith(youtubeURL1) or message.content.startswith(youtubeURL2):
                    source = "youtube.com/"

                    if f"{source}playlist?list=" in message.content:

                        playlist_id = message.content.replace("https://www.youtube.com/playlist?list=","")
                        video_id = message.content.replace("https://youtube.com/playlist?list=","")

                        try:

                            embed = await YouTube.PlaylistEmbed(playlist_id,message)

                        except findError:

                            error = True
                            errorType = "playlist"
                            error_url = f"https://www.youtube.com/playlist?list={playlist_id}"

                    elif f"{source}watch?v=" in message.content:

                        video_id = message.content.split("&")[0]
                        video_id = video_id.split("youtube.com/watch?v=")[1]

                        try:

                            embed = await YouTube.VideoEmbed(video_id,message)

                        except findError:

                            error = True
                            errorType = "video"
                            error_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    elif f"{source}channel/" in message.content:

                        channel_id = message.content.split("youtube.com/channel/")[1]
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

                    await asyncio.sleep(0.5)
                    await message.delete()

                    if source != "unsupported" and botMsg != None:
                        await botMsg.add_reaction(upvote)
                        await botMsg.add_reaction(downvote)

    songinfo_options = [{"name":"url","description":"The Spotify URL of the song.","type":3,"required":"true"}]
    @cog_ext.cog_slash(name="songinfo", description="Gives info about a Spotify song.", options=songinfo_options)
    async def slash_songinfo(self, ctx, url):

        if url.startswith(spotifyURL1) == True or url.startswith(spotifyURL2) == True:

            id = url.replace(f"{spotifyURL1}track/","")
            id = id.replace(f"{spotifyURL2}track/","")
            id = id.split("?")[0]

            track = sp.track(id)
            print(track)
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