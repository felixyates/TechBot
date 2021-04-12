import discord, os, asyncio, requests, base64, json
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.embedvars import setembedvar
from modules.emoji import upvote,downvote,nope

## Send a YouTube / Spotify URL and TechBot will react with upvote and downvote
## Future versions will delete the original message and send an embed with:
    ## Album art
    ## Track/playlist length
    ## Recommended by
    ## Etc.


global spotifyColour, youtubeColour
spotifyColour = 0x1db954
youtubeColour = 0xe62117


with open('/home/pi/spotify_secret.txt','r') as file:
    client_secret = str(file.readlines()[0])

with open('/home/pi/spotify_client_id.txt','r') as file:
    client_id = str(file.readlines()[0])


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
    print(res)

    responseObject = res.json()
    #print(json.dumps(responseObject, indent=2))

    accessToken = responseObject['access_token']
    return accessToken



def getSpotifyInfo(accessToken,type,id):

    endpoint = f"https://api.spotify.com/v1/{type}/{id}"
    print(endpoint)

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

    replaceList = [['&amp;','&'],['&#x2F;','/']]

    # Setting all variables using playlist object

    name = playlist["name"]
    url = playlist["external_urls"]["spotify"]
    trackTotal = playlist["tracks"]["total"]
    followers = playlist["followers"]["total"]
    description = playlist["description"]
    imageurl = playlist["images"]
    imageurl = imageurl[(len(imageurl)-1)]["url"]

    # Cleaning up playlist description (Spotify handles characters weirdly).

    if description.startswith('<a href='):
        description = ""
    else:
        description = description.split('<a href="')
        description = str(description[0])
        print(description)
        for i in range(len(replaceList)):
            if replaceList[i][0] in description:
                description.replace(replaceList[i][0], replaceList[i][1])
                print(description)
    
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
        remainingTracks = (len(trackList)) - 5
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

    mainArtist_icon = mainArtistObject["images"]
    mainArtist_icon = mainArtist_icon[(len(mainArtist_icon)-1)]["url"]

    # Using message.author for footer

    authorName = message.author.display_name
    authorAvatar = message.author.avatar_url

    embed=discord.Embed(title=albumName, url=albumURL, color=spotifyColour)
    embed.set_author(name=mainArtistName, url=mainArtistURL, icon_url=mainArtist_icon)
    embed.set_thumbnail(url=album_icon)
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

    mainArtist_icon = mainArtistObject["images"]
    mainArtist_icon = mainArtist_icon[(len(mainArtist_icon)-1)]["url"]

    # Using message.author for footer

    authorName = message.author.display_name
    authorAvatar = message.author.avatar_url

    # Getting album information and cover image.

    album = track["album"]
    album_name = album["name"]
    album_image = album["images"]
    album_image = album_image[(len(album_image)-1)]["url"]

    # Setting up embed.

    embed=discord.Embed(title=name, url=url, color=spotifyColour)
    embed.set_author(name=mainArtistName, url=mainArtistURL, icon_url=mainArtist_icon)
    embed.set_thumbnail(url=album_image)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Album", value=f"[{album_name}](https://open.spotify.com/album/{album['uri'].strip('spotify:album:')}/)", inline=True)

    # Handling multiple artists (if present).

    artistVar = ""

    if len(artists) > 1:
        for i in range(1,len(artistsName)):
            artistVar = artistVar + "\n"+ f"[{artistsName[i][0]}]({artistsName[i][1]})"
        embed.add_field(name="Other Artists", value=artistVar)

    # Adding footer and returning embed.

    embed.set_footer(text=f"Song recommended by {authorName}",icon_url=authorAvatar)
    return embed

class Music(commands.Cog, name="music"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        guild = 788802564912709692 # techbot
        channel = 825351987495043082 # music
        if (message.guild.id == guild) and (message.channel.id == channel) and (message.author.bot == False):
            
            # Determines data source to pull track / playlist info from

            if message.content.startswith("https://open.spotify.com/"):
                source = "spotify"
            elif message.content.startswith("https://youtube.com/"):
                source = "youtube"
            else:
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
                

            if source == "spotify":
                if "https://open.spotify.com/playlist/" in message.content:
                    playlist_id = message.content.replace("https://open.spotify.com/playlist/","")
                    accessToken = getAccessToken(client_id, client_secret)
                    playlist = getSpotifyInfo(accessToken,"playlists",playlist_id)
                    playlistEmbed = spotifyPlaylistEmbed(playlist,message)
                    botMsg = await message.channel.send(embed=playlistEmbed)
                elif "https://open.spotify.com/track/" in message.content:
                    track_id = message.content.replace("https://open.spotify.com/track/","")
                    track_id = track_id.split("?")[0]
                    accessToken = getAccessToken(client_id, client_secret)
                    track = getSpotifyInfo(accessToken,"tracks",track_id)
                    trackEmbed = spotifyTrackEmbed(track,message)
                    botMsg = await message.channel.send(embed=trackEmbed)
                elif "https://open.spotify.com/artist/" in message.content:
                    artist_id = message.content.replace("https://open.spotify.com/artist/","")
                    artist_id = artist_id.split("?")[0]
                    accessToken = getAccessToken(client_id, client_secret)
                    artist = getSpotifyInfo(accessToken,"artists",artist_id)
                    artistEmbed = spotifyArtistEmbed(artist,message)
                    botMsg = await message.channel.send(embed=artistEmbed)
                elif "https://open.spotify.com/album/" in message.content:
                    album_id = message.content.replace("https://open.spotify.com/album/","")
                    album_id = album_id.split("?")[0]
                    accessToken = getAccessToken(client_id, client_secret)
                    album = getSpotifyInfo(accessToken,"albums",album_id)
                    albumEmbed = spotifyAlbumEmbed(album,message)
                    botMsg = await message.channel.send(embed=albumEmbed)
            elif source == "youtube":
                if "https://www.youtube.com/playlist?list=" in message.content:
                    playlist_id = message.content.replace("https://www.youtube.com/playlist?list=","")
                    ## Need to finish
            await message.delete()
            await botMsg.add_reaction(upvote)
            await botMsg.add_reaction(downvote)

def setup(bot):
    bot.add_cog(Music(bot))