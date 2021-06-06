import discord, os, asyncio, requests, base64, json, spotipy
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import upvote,downvote,nope
from modules.getjson import secret, loadServerJson
from spotipy import SpotifyClientCredentials

## Send a YouTube / Spotify URL and TechBot will react with upvote and downvote
## Future versions will delete the original message and send an embed with:
    ## Album art
    ## Track/playlist length
    ## Recommended by
    ## Etc.


global spotifyColour, youtubeColour
spotifyColour = 0x1db954
youtubeColour = 0xe62117

spotify = secret("spotify")
client_secret = spotify["private"]
client_id = spotify["public"]

yt_api_key = secret("youtube")

class findError(Exception):
    pass



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



def getYouTubeData(id,type):

    if type == "video":
        endpoint = f"https://www.googleapis.com/youtube/v3/videos?part=snippet%2Cstatistics%2CcontentDetails&id={id}&key={yt_api_key}"

    elif type == "channel":
        endpoint = f"https://www.googleapis.com/youtube/v3/channels?part=snippet%2Cstatistics&id={id}&key={yt_api_key}"

    elif type == "playlist":
        endpoint = f"https://www.googleapis.com/youtube/v3/playlists?part=contentDetails%2Csnippet&2Cstatistics&id={id}&key={yt_api_key}"

    res = requests.get(endpoint)
    print(res)
    responseObject = res.json()
    return responseObject



def youtubeVideoEmbed(video_id,message):

    video = getYouTubeData(video_id,"video")
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

        channel = getYouTubeData(channelID,"channel")

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
        embed = setembedvar("R","Error getting video details",f"[Recommended video]({video_url}) is private or was not found.")
        embed.set_footer(text=f"Failed recommendation by {message.author.display_name}",icon_url=message.author.avatar_url)
    return embed



def youtubePlaylistEmbed(playlist_id, message):

    playlist = getYouTubeData(playlist_id,"playlist")
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

    if len(playlist["items"]) != 0:
        snippet = playlist["items"][0]["snippet"]
        title = snippet["title"]
        description = snippet["description"]
        thumbnail = snippet["thumbnails"]["default"]["url"]
        videos = playlist["items"][0]["contentDetails"]["itemCount"]

        channelID = snippet["channelId"]
        channelTitle = snippet["channelTitle"]

        channel = getYouTubeData(channelID,"channel")

        channelIcon = channel["items"][0]["snippet"]["thumbnails"]["default"]["url"]
        channelURL = f"https://www.youtube.com/channel/{channelID}"

        embed=discord.Embed(title=title, url=playlist_url, description=description, color=youtubeColour)
        embed.set_author(name=channelTitle, url=channelURL, icon_url=channelIcon)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Videos", value=videos, inline=True)
        embed.set_footer(text=f"Playlist recommended by {message.author.display_name}",icon_url=message.author.avatar_url)
    else:
        raise findError
        embed = setembedvar("R","Error getting playlist details",f"[Recommended playlist]({playlist_url}) is private or was not found.")
        embed.set_footer(text=f"Failed recommendation by {message.author.display_name}",icon_url=message.author.avatar_url)
    return embed



def youtubeChannelEmbed(channel_id, message):
    
    channel = getYouTubeData(channel_id,"channel")
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



def getAccessToken(client_id, client_secret):

    authURL = "https://accounts.spotify.com/api/token"
    authHeader = {}
    authData = {}

    # Base64 Encoded Client ID and Client Secret

    message = f"{client_id}:{client_secret}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    authHeader['Authorization'] = "Basic " + base64_message
    authData['grant_type'] = "client_credentials"
    res = requests.post(authURL, headers=authHeader, data=authData)

    responseObject = res.json()
    accessToken = responseObject['access_token']
    return accessToken



def getSpotifyInfo(accessToken, type="", id="", endpoint=""):

    if endpoint == "":

        endpoint = f"https://api.spotify.com/v1/{type}/{id}"

    getHeader = {
        "Authorization": "Bearer " + accessToken
    }

    res = requests.get(endpoint, headers=getHeader)
    
    try:
        Object = res.json()
        return Object
    except ValueError:
        print("Decoding JSON failed.")



def spotifyArtistEmbed(artist,message):

    # Setting all artist variables using artist object

    followers = artist["followers"]["total"]
    popularity = artist["popularity"]
    artistName = artist["name"]
    artistURL = artist["external_urls"]["spotify"]
    artist_icon = artist["images"]
    artist_icon = artist_icon[(len(artist_icon)-1)]["url"]

    # Fetching artist's 10 most popular songs.

    hasTopTracks = False

    try:

        market = "GB"
        tracks = getSpotifyInfo(getAccessToken(client_id, client_secret),"artists",f"{artist['id']}/top-tracks?market={market}")

        topTrack = tracks["tracks"][0]

        trackName = topTrack["name"]
        trackURL = topTrack["external_urls"]["spotify"]

        # Getting artist's top song album information and setting variables.

        albumName = topTrack["album"]["name"]
        albumURL = topTrack["album"]["external_urls"]["spotify"]
        album_icon = topTrack["album"]["images"]
        album_icon = album_icon[(len(album_icon)-1)]["url"]

        hasTopTracks = True

    except:

        # Otherwise, use artist image as album icon and display message.
        # I will make it display latest release instead in future.

        album_icon = artist_icon
    
    # Using message.author for footer

    authorName = message.author.display_name
    authorAvatar = message.author.avatar_url

    # Setting up embed

    if hasTopTracks == True:
        embed=discord.Embed(title=trackName, url=trackURL, description="Most popular song (USA)\n"+f"From [{albumName}]({albumURL})", color=spotifyColour)
    else:
        embed=discord.Embed(title="", description="Artist does not have enough plays for top songs.", color=spotifyColour)

    embed.set_author(name=artistName, url=artistURL, icon_url=artist_icon)
    embed.set_thumbnail(url=album_icon)
    embed.add_field(name="Followers", value=followers, inline=True)
    embed.add_field(name="Artist Popularity", value=f"{popularity}%", inline=True)
    embed.set_footer(text=f"Artist recommended by {authorName}",icon_url=authorAvatar)
    return embed



def spotifyPlaylistEmbed(playlist,message):

    # Setting all variables using playlist object

    name = playlist["name"]
    url = playlist["external_urls"]["spotify"]
    trackTotal = playlist["tracks"]["total"]
    followers = playlist["followers"]["total"]
    description = playlist["description"]
    imageurl = playlist["images"]
    imageurl = imageurl[(len(imageurl)-1)]["url"]

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

    owner = playlist["owner"]
    ownerID = str(owner["id"])
    ownerName = owner["display_name"]

    # Using owner object to get playlist owner URL and icon.

    ownerObject = getSpotifyInfo(getAccessToken(client_id, client_secret),"users",ownerID)
    ownerURL = ownerObject["external_urls"]["spotify"]
    owner_icon = ownerObject["images"]
    owner_icon = owner_icon[(len(owner_icon)-1)]["url"]

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



def spotifyAlbumEmbed(album,message):

    # Using album object to set variables.

    albumName = album["name"]
    albumURL = album["external_urls"]["spotify"]
    albumReleaseDate = album["release_date"]
    albumTracks = album["tracks"]["total"]
    album_icon = album["images"]
    album_icon = album_icon[(len(album_icon)-1)]["url"]

    # Getting track list

    trackList = []

    for x in range(len(album["tracks"]["items"])):
        trackList.append(album["tracks"]["items"][x]["name"])
    
    # Formatting track list

    formattedTrackList = ""

    for i in range(len(trackList)):
        if i < 5:
            formattedTrackList += f"{i+1}. `{str(trackList[i])}`" + "\n"

    if len(trackList) > 5:
        remainingTracks = albumTracks - 5
        formattedTrackList += f"+ {remainingTracks} more songs..."

    # Getting artist information.

    artists = album["artists"]
    artistsName = []

    
    mainArtist = album["artists"][0]
    mainArtistID = mainArtist["id"]
    mainArtistName = mainArtist["name"]
    mainArtistURL = mainArtist["external_urls"]["spotify"]
    mainArtistObject = getSpotifyInfo(getAccessToken(client_id, client_secret),"artists",mainArtistID)
    

    for i in range(len(artists)):
        artistID = artists[i]["id"]
        artistObject = getSpotifyInfo(getAccessToken(client_id, client_secret),"artists",artistID)
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

    # Setting up embed

    embed = setembedvar(spotifyColour, albumName, url=albumURL, author=mainArtistName, author_url=mainArtistURL, author_icon=mainArtist_icon, thumbnail=album_icon)
    embed.add_field(name="Release Date", value=albumReleaseDate, inline=True)
    embed.add_field(name="Tracks", value=albumTracks, inline=True)
    embed.add_field(name="Track List", value=formattedTrackList, inline=False)
    embed.set_footer(text=f"Album recommended by {authorName}",icon_url=authorAvatar)

    # Handling multiple artists (if present).

    artistVar = ""

    if len(artists) > 1:
        for i in range(1,len(artistsName)):
            artistVar = artistVar + "\n"+ f"[{artistsName[i][0]}]({artistsName[i][1]})"
        embed.add_field(name="Other Artists", value=artistVar)

    return embed



def spotifyTrackEmbed(track,message):

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
    mainArtistObject = getSpotifyInfo(getAccessToken(client_id, client_secret),"artists",mainArtistID)
    

    for i in range(len(artists)):
        artistID = artists[i]["id"]
        artistObject = getSpotifyInfo(getAccessToken(client_id, client_secret),"artists",artistID)
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



def spotifyUserEmbed(user,message):
    
    display_name = user["display_name"]
    url = user["external_urls"]["spotify"]
    followers = user["followers"]["total"]

    try:
        pfp = user["images"][0]["url"]
    except:
        pfp = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"

    accessToken = getAccessToken(client_id, client_secret)
    playlists = getSpotifyInfo(accessToken, endpoint = f"https://api.spotify.com/v1/users/{user['id']}/playlists?limit=5")

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



class Music(commands.Cog, name="music"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):

        if message.author.bot == False and message.guild != None:

            servers = loadServerJson()
            music = servers[str(message.guild.id)]["music"]
            enabled = music["enabled"]
            channel = music["channel"]

            if (message.channel.id == int(channel)) and (enabled == 1):
            
                # Determines data source to pull info from

                spotifyURL1 = "https://open.spotify.com/"
                spotifyURL2 = "https://www.open.spotify.com/"
                youtubeURL1 = "https://www.youtube.com/"
                youtubeURL2 = "https://youtube.com/"


                if message.content.startswith(spotifyURL1) or message.content.startswith(spotifyURL2):
                    source = "spotify"

                elif message.content.startswith(youtubeURL1) or message.content.startswith(youtubeURL2):
                    source = "youtube"

                elif message.content.startswith("https://") and not (message.content.startswith(spotifyURL1) or message.content.startswith(youtubeURL1) or message.content.startswith(youtubeURL2) or message.content.startswith(spotifyURL2)):
                    source = "unsupported"

                    unsupportedVar = setembedvar("R","Unsupported Source",f"{nope} Please send only YouTube or Spotify URLs."+"\nSee below for examples of valid links:",False)

                    spotifyExamples = """`https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC`
                    `https://open.spotify.com/album/6N9PS4QXF1D0OWPk0Sxtb4`
                    `https://open.spotify.com/artist/0gxyHStUsqpMadRV0Di1Qt`
                    `https://open.spotify.com/playlist/6piHLVTmzq8nTix2wIlM8x`
                    *Note: don't worry about the `?si=` bit at the end of your URL; it doesn't matter.*"""
                    youtubeExamples = """`https://www.youtube.com/watch?v=dQw4w9WgXcQ`
                    `https://www.youtube.com/playlist?list=PLi9drqWffJ9FWBo7ZVOiaVy0UQQEm4IbP`"""

                    unsupportedVar.add_field(name="Spotify",value=spotifyExamples,inline=False)
                    unsupportedVar.add_field(name="YouTube",value=youtubeExamples,inline=False)

                    await message.channel.send(embed=unsupportedVar,delete_after=20)
            
                else:
                    source = "none"

                if source == "spotify":

                    if "open.spotify.com/playlist/" in message.content:
                        playlist_id = message.content.replace("https://www.open.spotify.com/playlist/","")
                        playlist_id = message.content.replace("https://open.spotify.com/playlist/","")
                        accessToken = getAccessToken(client_id, client_secret)
                        playlist = getSpotifyInfo(accessToken,"playlists",playlist_id)
                        playlistEmbed = spotifyPlaylistEmbed(playlist,message)
                        botMsg = await message.channel.send(embed=playlistEmbed)

                    elif "open.spotify.com/track/" in message.content:
                        track_id = message.content.replace("https://www.open.spotify.com/track/","")
                        track_id = message.content.replace("https://open.spotify.com/track/","")
                        track_id = track_id.split("?")[0]
                        accessToken = getAccessToken(client_id, client_secret)
                        track = getSpotifyInfo(accessToken,"tracks",track_id)
                        trackEmbed = spotifyTrackEmbed(track,message)
                        botMsg = await message.channel.send(embed=trackEmbed)

                    elif "open.spotify.com/artist/" in message.content:
                        artist_id = message.content.replace("https://www.open.spotify.com/artist/","")
                        artist_id = message.content.replace("https://open.spotify.com/artist/","")
                        artist_id = artist_id.split("?")[0]
                        accessToken = getAccessToken(client_id, client_secret)
                        artist = getSpotifyInfo(accessToken,"artists",artist_id)
                        artistEmbed = spotifyArtistEmbed(artist,message)
                        botMsg = await message.channel.send(embed=artistEmbed)

                    elif "open.spotify.com/album/" in message.content:
                        album_id = message.content.replace("https://www.open.spotify.com/album/","")
                        album_id = message.content.replace("https://open.spotify.com/album/","")
                        album_id = album_id.split("?")[0]
                        accessToken = getAccessToken(client_id, client_secret)
                        album = getSpotifyInfo(accessToken,"albums",album_id)
                        albumEmbed = spotifyAlbumEmbed(album,message)
                        botMsg = await message.channel.send(embed=albumEmbed)
                    
                    elif "open.spotify.com/user/" in message.content:
                        user_id = message.content.replace("https://www.open.spotify.com/user/","")
                        user_id = message.content.replace("https://open.spotify.com/user/","")
                        user_id = user_id.split("?")[0]
                        accessToken = getAccessToken(client_id, client_secret)
                        user = getSpotifyInfo(accessToken,"users",user_id)
                        userEmbed = spotifyUserEmbed(user,message)
                        botMsg = await message.channel.send(embed=userEmbed)

                elif source == "youtube":
                    
                    error = False
                    botMsg = None

                    if "youtube.com/playlist?list=" in message.content:
                        playlist_id = message.content.replace("https://www.youtube.com/playlist?list=","")
                        video_id = message.content.replace("https://youtube.com/playlist?list=","")
                        try:
                            embed = youtubePlaylistEmbed(playlist_id,message)
                        except findError:
                            error = True
                            errorType = "playlist"
                            error_url = f"https://www.youtube.com/playlist?list={playlist_id}"

                    elif "youtube.com/watch?v=" in message.content:
                        video_id = message.content.split("&")[0]
                        video_id = video_id.split("youtube.com/watch?v=")[1]
                        try:
                            embed = youtubeVideoEmbed(video_id,message)
                        except findError:
                            error = True
                            errorType = "video"
                            error_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    elif "youtube.com/channel/" in message.content:
                        channel_id = message.content.split("youtube.com/channel/")[1]
                        try:
                            embed = youtubeChannelEmbed(channel_id, message)
                        except findError:
                            error = True
                            errorType = "channel"
                            error_url = f"https://www.youtube.com/channel/{channel_id}"

                    else:
                        source = "none"
                    
                    if error == True:
                        embed = setembedvar("R",f"Error getting {errorType} details",f"[Recommended {errorType}]({error_url}) is private or was not found.")
                        embed.set_footer(text=f"Failed recommendation by {message.author.display_name}",icon_url=message.author.avatar_url)
                        errorMsg = await message.channel.send(embed=embed, delete_after=7.5)
                    else:
                        botMsg = await message.channel.send(embed=embed)

                if source != "none":
                    await asyncio.sleep(0.5)
                    await message.delete()
                    if source != "unsupported" and botMsg != None:
                        await botMsg.add_reaction(upvote)
                        await botMsg.add_reaction(downvote)

def setup(bot):
    bot.add_cog(Music(bot))