import discord, spotipy
from modules.getjson import secret
from modules import embs
from spotipy import SpotifyClientCredentials

URL1, URL2, DEFAULTPFP = "https://open.spotify.com/", "https://www.open.spotify.com/", "https://developer.spotify.com/assets/branding-guidelines/icon4@2x.png"
COLOUR = 0x1db954
spotify = secret("spotify")
sp = spotipy.Spotify(auth_manager = SpotifyClientCredentials(client_id = spotify["public"], client_secret = spotify["private"]))

class Subclass:
    def __init__(self, dict: dict):
        for (key, value) in dict.items():
            if key in ["popularity", "danceability", "energy"]:
                value = Object.ToPercent(self, value)
            elif key == "tempo":
                value = round(value)
            setattr(self, key, value)

class SpEmbed(embs.Embed):
    def __init__(self, **kwargs):
        kwargs["color"] = COLOUR
        super().__init__(**kwargs)
    
    async def SetFooter(self, author: discord.User):
        self.add_field(name = 'Recommended by', value = author.mention)
        self.set_footer(text="Data: Spotify", icon_url=author.avatar.url)

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

class Object:
    def __init__(self, id):
        self.id = id
    
    def ToPercent(self, value: float):
        if value < 1:
            return f"{round(value*100)}%"
        else:
            return f"{round(value)}%"

    def AttributeSetter(self, attrs: dict):
        for (key, value) in attrs.items():
            if key == "external_urls":
                self.url = value["spotify"]
            elif key == "followers":
                self.followers = value["total"]
            elif key == "images":
                if len(value) > 0:
                    self.icon = value[0]["url"]
                else:
                    self.icon = DEFAULTPFP
            elif key == "owner":
                self.owner = value["id"]
            elif key == "duration_ms":
                self.duration = Funcs.durationFormatter(value)
            elif type(value) == dict:
                setattr(self, key, Subclass(value))
            else:
                setattr(self, key, value)
        
    def DescCleanup(self):
        """Cleaning up playlist description (Spotify handles characters weirdly).
        - Need to work on this - it doesn't work."""

        replaceList = [['&amp;','&'],['&#x2F;','/']]

        if self.description.startswith('<a href='):
            self.description = ""
        else:
            self.description = self.description.split('<a href="')
            self.description = str(self.description[0])
            for i in range(len(replaceList)):
                if replaceList[i][0] in self.description:
                    self.description.replace(replaceList[i][0], replaceList[i][1])

class Spotify:
    class Track(Object):
        def __init__(self, id):
            track = sp.track(id)
            self.AttributeSetter(track)
            self.adv = Subclass(sp.audio_features(id)[0])
            self.mainArtist = Spotify.Artist(self.artists[0]["id"])
            self.album = Spotify.Album(track["album"]["id"])

        async def GetEmbed(self, author):
            embed = SpEmbed(title = self.name, url = self.url, thumbnail = self.album.icon)
            embed.set_author(name = self.mainArtist.name, url = self.mainArtist.url, icon_url = self.mainArtist.icon)
            self, embed = Funcs.multipleArtistHandler(self, self.artists, embed)
            fields = [
                ["Duration", self.duration],
                ["Danceability", self.adv.danceability],
                ["Energy", self.adv.energy],
                ["Key", self.adv.key],
                ["Tempo", self.adv.tempo],
                ["Album",f"[{self.album.name}]({URL1}/album/{self.album.id.strip('spotify:album:')}/)"]
            ]
            if self.preview_url is not None:
                fields.append(["Preview",f"[Download]({self.preview_url})"])
            embed.AddFields(fields)
            await embed.SetFooter(author)
            return embed

    class TopTrack(Track):
        def __init__(self, id):
            tracks = sp.artist_top_tracks(id)["tracks"]

            if len(tracks) > 0:
                self.track = tracks[0]
                self.AttributeSetter(self.track)
                self.album = Spotify.Album(self.album.uri)

        async def GetEmbed(self):
            if hasattr(self, "track"):
                return SpEmbed(
                    title = self.name,
                    url = self.url,
                    description = f"""Most popular song (USA)
                    on [{self.album.name}]({self.album.url})"""
                )
            else:
                return SpEmbed(description="Artist does not have enough plays for top songs.")

    class Artist(Object):
        def __init__(self, id):
            artist = sp.artist(id)
            self.AttributeSetter(artist)
            try:
                self.icon = artist["images"][0]["url"]
            except:
                self.icon = DEFAULTPFP

        async def GetEmbed(self, author):
                self.topTrack = Spotify.TopTrack(self.id)
                embed = await self.topTrack.GetEmbed()
                embed.set_author(name = self.name, url = self.url, icon_url = self.icon)
                embed.set_thumbnail(url = self.topTrack.album.icon)
                embed.AddFields([['Followers', self.followers], ['Popularity', self.popularity]])
                await embed.SetFooter(author)
                return embed

    class Playlist(Object):
        def __init__(self, id):
            self.AttributeSetter(sp.playlist(id))
            self.DescCleanup()
            # Getting playlist owner information.
            ownerID = str(self.owner)
            # Using owner info to get playlist owner URL and icon.
            self.owner = Spotify.User(ownerID)

        async def GetEmbed(self, author):
            embed = SpEmbed(title = self.name, url = self.url, description = self.description)
            embed.set_author(name = self.owner.name, url = self.owner.url, icon_url= self.owner.pfp)
            embed.set_thumbnail(url = self.icon)
            fields = [["Tracks", self.tracks.total],["Followers", self.followers]]
            embed.AddFields(fields)
            await embed.SetFooter(author)
            return embed

    class Album(Object):
        def __init__(self, id):
            album = sp.album(id)
            trackItems = album["tracks"]["items"]
            trackList = []
            self.AttributeSetter(sp.album(id))
            self.mainArtist = Spotify.Artist(self.artists[0]["id"])

            for x in range(len(trackItems)):
                trackList.append(trackItems[x])

            self.formattedTrackList = ""

            for i in range(len(trackList)):
                if i < 5:
                    self.formattedTrackList += f"{i+1}. [{trackList[i]['name']}]({trackList[i]['external_urls']['spotify']})" + "\n"

            if len(trackList) > 5:
                remainingTracks = self.tracks.total - 5
                self.formattedTrackList += f"+ {remainingTracks} more songs..."

        async def GetEmbed(self, author):
            embed = SpEmbed(title = self.name, url = self.url)
            embed.set_author(name = self.mainArtist.name, url = self.mainArtist.url, icon_url = self.mainArtist.icon)
            embed.set_thumbnail(url = self.icon)
            self, embed = Funcs.multipleArtistHandler(self, self.artists, embed)
            fields = [["Release Date", self.release_date], ["Tracks", self.tracks.total], ["Track List", self.formattedTrackList, False]]
            embed.AddFields(fields)
            await embed.SetFooter(author)
            return embed

    class User(Object):
        def __init__(self, id):    
            self.AttributeSetter(sp.user(id))
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
        
        async def GetEmbed(self, author):
            user = self
            fields = [["Followers", user.followers]]
            embed = SpEmbed()
            embed.set_author(name = user.name, url = user.url, icon_url = user.pfp)

            if self.has_playlists:
                embed.set_thumbnail(user.firstPlaylistThumbnail)
                fields.append(["Public Playlists", user.playlistStr])
            else:
                fields.append(["No Public Playlists", "Make sure they're public."])

            embed.AddFields(fields)
            await embed.SetFooter(author)
            return embed
