import discord, pyyoutube
from modules.getjson import secret
from modules import embs

URL1, URL2 = "https://www.youtube.com/", "https://youtube.com/"
COLOUR = 0xe62117
yt = pyyoutube.Api(api_key = secret("youtube"))

SOURCE = "youtube.com/"
PLAYLISTURL = f"{SOURCE}playlist?list="
VIDEOURL = f"{SOURCE}watch?v="
CHANNELURL = f"{SOURCE}channel/"

class findError(Exception):
    pass

class Subclass:
    def __init__(self, attrs: dict):
        for (key, value) in attrs.items():
            if type(value) == dict:
                value = Subclass(value)
            setattr(self, key, value)

class Funcs():
    def DurationFormatter(duration):
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
        return duration

class Object:
    def __init__(self, content: str):
        if PLAYLISTURL in content:
            self.type = "playlist"
            self.id = content.split("playlist?list=")[1]
        elif VIDEOURL in content:
            self.type = "video"
            self.id = content.split("&")[0].split("watch?v=")[1]
        elif CHANNELURL in content:
            self.type = "channel"
            self.id = content.split("channel/")[1]
        else:
            self.type = None

    async def Get(self):
        if self.type == "playlist":
            return Playlist(self.id)
        elif self.type == "video":
            return Video(self.id)
        elif self.type == "channel":
            return Channel(self.id)
        else:
            raise findError
    
    def AttributeSetter(self, attrs: dict):
        for (key, value) in attrs.items():
            if key == "snippet":
                self.icon = value["thumbnails"]["default"]["url"]
            if type(value) == dict:
                value = Subclass(value)
            elif type(value) == list:
                self.AttributeSetter(value[0])
            setattr(self, key, value)

    class Embed(embs.Embed):
        def __init__(self, **kwargs):
            super().__init__(**kwargs, colour = COLOUR)

        def SetFooter(self, author: discord.User):
            self.set_footer(text = f"Recommended by {author.display_name} • Data: YouTube", icon_url = author.avatar.url)

class Video(Object):
    def __init__(self, id: str):
        video = yt.get_video_by_id(video_id = id).to_dict()
        self.url = f"https://www.youtube.com/watch?v={id}"
        if len(video["items"]) > 0:
            video = video["items"][0]
            self.AttributeSetter(video)
            self.duration = Funcs.DurationFormatter(self.contentDetails.duration)
            self.channel = Channel(self.snippet.channelId)
        else:
            raise findError

    async def GetEmbed(self, author):
        embed = self.Embed(title = self.snippet.title, url = self.url)
        embed.set_author(name = self.channel.snippet.title, url = self.channel.url, icon_url = self.channel.icon)
        embed.set_thumbnail(url = self.icon)
        fields = [["Views", self.statistics.viewCount],["Likes", self.statistics.likeCount], ["Duration", self.duration]]
        embed.AddFields(fields)
        embed.SetFooter(author)
        return embed

class Playlist(Object):
    def __init__(self, id):
        playlist = yt.get_playlist_by_id(playlist_id = id).to_dict()
        self.url = f"https://www.youtube.com/playlist?list={id}"
        if len(playlist["items"]) > 0:
            self.AttributeSetter(playlist["items"][0])
            self.channel = Channel(self.snippet.channelId)
        else:
            raise findError

    async def GetEmbed(self, author):
        embed = self.Embed(title = self.snippet.title, url = self.url, description = self.snippet.description)
        embed.set_author(name = self.channel.snippet.title, url = self.channel.url, icon_url = self.channel.icon)
        embed.set_thumbnail(url = self.icon)
        embed.AddFields([["Videos", self.contentDetails.itemCount]])
        embed.SetFooter(author)
        return embed

class Channel(Object):
    def __init__(self, id):
        channel = yt.get_channel_info(channel_id = id).to_dict()
        self.url = f"https://www.youtube.com/channel/{id}"

        if channel["pageInfo"]["totalResults"] > 0:
            channel = channel["items"][0]
            self.AttributeSetter(channel)
        else:
            raise findError

    async def GetEmbed(self, author):
            embed = self.Embed(description = self.snippet.description)
            embed.set_author(name = self.snippet.title, url = self.url, icon_url = self.icon)
            fields = [
                ["Subscribers", self.statistics.subscriberCount],
                ["Videos", self.statistics.videoCount],
                ["Total Views", self.statistics.viewCount]
            ]
            embed.AddFields(fields)
            embed.SetFooter(author)
            return embed