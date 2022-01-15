import discord, spotipy
from modules.getjson import secret
from modules.embedvars import setembedvar
from spotipy import SpotifyClientCredentials

URL1, URL2, defaultPfp = "https://open.spotify.com/", "https://www.open.spotify.com/", "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"
colour = 0x1db954
spotify = secret("spotify")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id = spotify["public"], client_secret = spotify["private"]))

class Funcs():

    async def idGetter(messageContent: str, contentType: str):

        id = messageContent.replace(f"{URL1}{contentType}/","")
        id = id.replace(f"{URL2}{contentType}/","")
        id = id.split("?")[0]
        return id

    def durationFormatter(durationMs):

        durationSecs = (durationMs/1000)
        durationMins = durationSecs // 60
        remainderSecs = round(durationSecs - (durationMins*60))

        if remainderSecs < 10:
            remainderSecs = f"0{remainderSecs}"

        return f"{int(durationMins)}:{remainderSecs}"

    def multipleArtistHandler(self, artists, embed):
            newArtists = []
            
            for artist in artists:
                tempArtist = [artist["name"], artist["external_urls"]["spotify"]]
                newArtists.append(tempArtist)
            
            artistVar = ""

            if len(artists) > 1:
                for i in range(1,len(newArtists)):
                    artistVar = artistVar + "\n"+ f"[{newArtists[i][0]}]({newArtists[i][1]})"
            
            if artistVar != "":
                embed.add_field(name="Other Artists", value=artistVar)
            
            return self, embed

    async def SetFooter(embed: discord.Embed, author: discord.User, type: str):
        embed.set_footer(text=f"{type} recommended by {author.display_name} • Data: Spotify",icon_url=author.avatar_url)
        return embed

class TopTrack():

    def __init__(self, id):
        tracks = sp.artist_top_tracks(id)["tracks"]

        if len(tracks) > 0:

            self.has = True
            track = tracks[0]
            self.name = track["name"]
            self.url = track["external_urls"]["spotify"]
            self.album = Album(track["album"]["uri"])
        else:
            self.has = False
            self.album.icon = ""

    async def getEmbed(self):
        if self.has == True:
            return discord.Embed(title = self.name, url = self.url, description = "Most popular song (USA)\n"+f"on [{self.album.name}]({self.album.url})", color= colour)
        else:
            return discord.Embed(title="", description="Artist does not have enough plays for top songs.", color= colour)

class Artist():

    def __init__(self, id):
        artist = sp.artist(id)
        self.id = artist["id"]
        self.name = artist["name"]
        self.url = artist["external_urls"]["spotify"]
        self.followers = artist["followers"]["total"]
        self.popularity = f"{artist['popularity']}%"

        try:
            self.icon = artist["images"][0]["url"]
        except:
            self.icon = defaultPfp

    async def getEmbed(self, author):
            self.topTrack = TopTrack(self.id)
            embed = await self.topTrack.getEmbed()
            embed.set_author(name = self.name, url = self.url, icon_url = self.icon)
            embed.set_thumbnail(url = self.topTrack.album.icon)
            embed.add_field(name="Followers", value = self.followers, inline=True)
            embed.add_field(name="Artist Popularity", value = self.popularity, inline=True)
            embed = await Funcs.SetFooter(embed, author, "Artist")
            return embed

class Playlist():

    def __init__(self, id):
        playlist = sp.playlist(id)
        self.name = playlist["name"]
        self.description = playlist["description"]
        self.url = playlist["external_urls"]["spotify"]
        self.followers = playlist["followers"]["total"]
        self.tracks = playlist["tracks"]["total"]
        self.owner = playlist["owner"]["id"]

        try:
            self.imageurl = playlist["images"][0]["url"]
        except:
            self.imageurl = ""

        # Cleaning up playlist description (Spotify handles characters weirdly).
            # Need to work on this - it doesn't work.

        replaceList = [['&amp;','&'],['&#x2F;','/']]

        if self.description.startswith('<a href='):
            self.description = ""
        else:
            self.description = self.description.split('<a href="')
            self.description = str(self.description[0])
            for i in range(len(replaceList)):
                if replaceList[i][0] in self.description:
                    self.description.replace(replaceList[i][0], replaceList[i][1])

        # Getting playlist owner information.

        ownerID = str(self.owner)

        # Using owner info to get playlist owner URL and icon.

        self.owner = User(ownerID)

    async def getEmbed(self, author):
        pl = self
        embed=discord.Embed(title= pl.name, url= pl.url, description = pl.description, color=colour)
        embed.set_author(name= pl.owner.name, url= pl.owner.url, icon_url= pl.owner.pfp)
        embed.set_thumbnail(url= pl.imageurl)
        embed.add_field(name="Tracks", value= pl.tracks, inline=True)
        embed.add_field(name="Followers", value= pl.followers, inline=True)
        embed = await Funcs.SetFooter(embed, author, "Playlist")
        return embed

class Album():

    def __init__(self, id):
        album = sp.album(id)
        self.name = album["name"]
        self.url = album["external_urls"]["spotify"]
        self.release_date = album["release_date"]
        self.tracks = album["tracks"]["total"]
        self.icon = album["images"][0]["url"]
        self.artists = album["artists"]
        self.mainArtist = Artist(self.artists[0]["id"])
        self.id = album["id"]

        trackList = []
        trackItems = album["tracks"]["items"]

        for x in range(len(trackItems)):
            trackList.append(trackItems[x])

        self.formattedTrackList = ""

        for i in range(len(trackList)):
            if i < 5:
                self.formattedTrackList += f"{i+1}. [{trackList[i]['name']}]({trackList[i]['external_urls']['spotify']})" + "\n"

        if len(trackList) > 5:
            remainingTracks = self.tracks - 5
            self.formattedTrackList += f"+ {remainingTracks} more songs..."

    async def getEmbed(self, author):
        embed = setembedvar(colour, self.name, url= self.url, author = self.mainArtist.name, author_url = self.mainArtist.url, author_icon = self.mainArtist.icon, thumbnail = self.icon)
        self, embed = Funcs.multipleArtistHandler(self, self.artists, embed)
        embed.add_field(name="Release Date", value = self.release_date)
        embed.add_field(name="Tracks", value = self.tracks)
        embed.add_field(name="Track List", value = self.formattedTrackList, inline = False)
        embed = await Funcs.SetFooter(embed, author, "Album")
        return embed

class User():

    def __init__(self, id):    
        user = sp.user(id)
        self.name = user["display_name"]
        self.url = user["external_urls"]["spotify"]
        self.followers = user["followers"]["total"]

        try:
            self.pfp = user["images"][0]["url"]
        except:
            self.pfp = defaultPfp

        self.playlists = sp.user_playlists(id, limit=5)

        playlistStr = ""
        pos = 0
        items = self.playlists["items"]
        self.has_playlists = False

        if len(items) > 0:

            self.has_playlists = True

            for x in items:

                pos += 1
                playlistStr = playlistStr + f"{pos}. [{x['name']}]({x['external_urls']['spotify']})" + "\n"

            remaining = self.playlists['total'] - pos

            if remaining > 0:

                self.playlistStr = playlistStr + f"+ {remaining} more"

            self.firstPlaylistThumbnail = self.playlists["items"][0]["images"][0]["url"]
    
    async def getEmbed(self, author):

        user = self

        if self.has_playlists:

            embed = setembedvar(colour, title="", author = user.name, author_url = user.url, author_icon = user.pfp, thumbnail = user.firstPlaylistThumbnail)
            embed.add_field(name = "Followers", value = user.followers)
            embed.add_field(name = "Public Playlists", value = user.playlistStr, inline=False)
    
        else:

            embed = setembedvar(colour, title="", author= user.name, author_url= user.url, author_icon= user.pfp)
            embed.add_field(name = "Followers", value = user.followers)
            embed.add_field(name = "No Public Playlists", value="Make sure they're public.", inline=False)

        embed = await Funcs.SetFooter(embed, author, "User")
        return embed

class Track():

    def __init__(self, id):
        track = sp.track(id)
        tr_adv = sp.audio_features(id)[0]
        self.name = track["name"]
        self.url = track["external_urls"]["spotify"]
        self.preview_url = track["preview_url"]
        self.duration = Funcs.durationFormatter(track["duration_ms"])
        self.artists = track["artists"]
        self.mainArtist = Artist(self.artists[0]["id"])
        self.album = Album(track["album"]["id"])
        danceability = f'{round(tr_adv["danceability"]*100, 1)}%'
        energy = f'{round(tr_adv["energy"]*100, 1)}%'
        key = tr_adv["key"]
        tempo = round(tr_adv["tempo"], 1)
        self.fields = [["Duration", self.duration], ["Danceability", danceability], ["Energy", energy], ["Key", key], ["Tempo", tempo]]

    async def getEmbed(self, author):
        embed = setembedvar(colour, self.name, url = self.url, author = self.mainArtist.name, author_url = self.mainArtist.url, author_icon = self.mainArtist.icon, thumbnail = self.album.icon)
        self, embed = Funcs.multipleArtistHandler(self, self.artists, embed)
        for field in self.fields:
            embed.add_field(name = field[0], value = field[1], inline = True)
        embed.add_field(name="Album", value=f"[{self.album.name}](https://open.spotify.com/album/{self.album.id.strip('spotify:album:')}/)", inline=True)

        if self.preview_url is not None:
            embed.add_field(name="Preview", value=f"[Download]({self.preview_url})", inline=True)

        embed = await Funcs.SetFooter(embed, author, "Track")
        return embed