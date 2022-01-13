import spotipy, asyncio, discord
from modules.getjson import secret, loadServerJson
from embedvars import setembedvar
from spotipy import SpotifyClientCredentials

class D2C(object):
    "Converts dictionary to class"
    def __init__(self, my_dict):
          
        for key in my_dict:
            setattr(self, key, my_dict[key])

global URL1, URL2, sp, defaultPfp, colour
URL1 = "https://open.spotify.com/"
URL2 = "https://www.open.spotify.com/"
defaultPfp = "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"
colour = 0xe62117
spotify = secret("spotify")
client_secret = spotify["private"]
client_id = spotify["public"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = spotify["public"], client_secret = spotify["private"]))

class Funcs(object):

    async def idGetter(messageContent: str, contentType: str):

        id = messageContent.replace(f"{URL1}{contentType}/","")
        print(id)
        id = id.replace(f"{URL2}{contentType}/","")
        print(id)
        id = id.split("?")[0]
        return id
    

class Embed(object):

    async def SetFooter(embed: discord.Embed, author: discord.User, type: str):

        embed.set_footer(text=f"{type} recommended by {author.display_name} • Data provided by Spotify.",icon_url=author.avatar_url)
        return embed

class TopTrack(id):

    def __init__(self, id):

        tracks = sp.artist_top_tracks(id)

        if len(tracks.tracks) > 0:

            track = tracks[0]
            self.name = track["name"]
            self.url = track["external_urls"]["spotify"]
            album = track["album"]
            self.album.name = album["name"]
            self.album.url = album["external_urls"]["spotify"]
            self.album.icon = album["images"][0]["url"]
            self.embed = discord.Embed(title = self.name, url = self.url, description = "Most popular song (USA)\n"+f"on [{self.album.name}]({self.album.url})", color= colour)

        else:

            self.album.icon = ""
            self.embed = discord.Embed(title="", description="Artist does not have enough plays for top songs.", color= colour)

        return self

async def Artist(id, author):

    def __init__(self, id):

        artist = sp.artist(id)
        uri = artist.uri
        self.name = artist["name"]
        self.url = artist["external_urls"]["spotify"]
        topTrack = TopTrack(id)
        embed = topTrack.embed

        try:
            
            self.icon = artist["images"][0]["url"]

        except:

            self.icon = defaultPfp

        # Setting up embed

        embed.set_author(name = self.name, url = self.url, icon_url = self.icon)
        embed.set_thumbnail(url = self.url)
        embed.add_field(name="Followers", value= artist.followers['total'], inline=True)
        embed.add_field(name="Artist Popularity", value=f"{artist.popularity}%", inline=True)
        embed = Embed.SetFooter(embed, author, "Artist")
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
            owner_icon = defaultPfp

        # Setting up embed

        embed=discord.Embed(title= playlist.name, url= playlist.external_urls["spotify"], description=description, color=colour)
        embed.set_author(name= playlist.owner["display_name"], url= owner.external_urls["spotify"], icon_url= owner_icon)
        embed.set_thumbnail(url= imageurl)
        embed.add_field(name="Tracks", value= playlist.tracks["total"], inline=True)
        embed.add_field(name="Followers", value= playlist.followers["total"], inline=True)
        embed = Embed.SetFooter(embed, author, "Playlist")
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

        embed = setembedvar(colour, name, url= url, author = mainArtistName, author_url = mainArtistURL, author_icon = mainArtist_icon, thumbnail = icon)
        embed.add_field(name="Release Date", value = release_date)
        embed.add_field(name="Tracks", value = tracks)
        embed.add_field(name="Track List", value = formattedTrackList, inline = False)
        embed = await Embed.SetFooter(embed, author, "Album")

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

            embed = setembedvar(colour, title="", author=display_name, author_url=url, author_icon=pfp, thumbnail = firstPlaylistThumbnail)
            embed.add_field(name = "Followers", value = followers)
            embed.add_field(name = "Public Playlists", value = playlistStr, inline=False)
        
        else:

            embed = setembedvar(colour, title="", author=display_name, author_url=url, author_icon=pfp)
            embed.add_field(name = "Followers", value = followers)
            embed.add_field(name = "No Public Playlists", value="Make sure they're public.", inline=False)

        embed = Embed.SetFooter(embed, author, "User")
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
        
        embed = setembedvar(colour, name, url=url, author=mainArtistName, author_url=mainArtistURL, author_icon=mainArtist_icon, thumbnail=album_image)
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
        
        embed = Embed.SetFooter(embed, author, "Track")
        return embed