import discord, pyyoutube
from modules.getjson import secret

URL1, URL2 = "https://www.youtube.com/", "https://youtube.com/"
colour = 0xe62117
yt = pyyoutube.Api(api_key = secret("youtube"))

class findError(Exception):
    pass

class Funcs():

    def durationFormatter(duration):
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

    def SetFooter(embed: discord.Embed, author: discord.User, type: str):
        embed.set_footer(text=f"{type} recommended by {author.display_name} • Data: YouTube",icon_url=author.avatar_url)
        return embed 

class Video():

    def __init__(self, id):
        video = yt.get_video_by_id(video_id = id).to_dict()
        self.url = f"https://www.youtube.com/watch?v={id}"
        if len(video["items"]) != 0:
            snippet = video["items"][0]["snippet"]
            stats = video["items"][0]["statistics"]
            self.title = snippet["title"]
            self.thumbnail = snippet["thumbnails"]["default"]["url"]
            self.duration = Funcs.durationFormatter(video["items"][0]["contentDetails"]["duration"])
            self.channel = Channel(snippet["channelId"])
            self.views = stats["viewCount"]
            self.likes = stats["likeCount"]
            self.dislikes = stats["dislikeCount"]
        else:
            raise findError

    async def getEmbed(self, author):
        embed = discord.Embed(title = self.title, url = self.url, color = colour)
        embed.set_author(name = self.channel.title, url = self.channel.url, icon_url = self.channel.icon)
        embed.set_thumbnail(url = self.thumbnail)
        embed.add_field(name = "Views", value = self.views, inline = True)
        embed.add_field(name = "Likes", value = self.likes, inline = True)
        embed.add_field(name = "Dislikes", value = self.dislikes, inline = True)
        embed.add_field(name = "Duration", value = self.duration, inline = True)
        embed = Funcs.SetFooter(embed, author, "Video")
        return embed

class Playlist():

    def __init__(self, id):
        playlist = yt.get_playlist_by_id(playlist_id = id).to_dict()
        self.url = f"https://www.youtube.com/playlist?list={id}"
        if len(playlist["items"]) != 0:
            snippet = playlist["items"][0]["snippet"]
            self.title = snippet["title"]
            self.description = snippet["description"]
            self.thumbnail = snippet["thumbnails"]["default"]["url"]
            self.videos = playlist["items"][0]["contentDetails"]["itemCount"]
            self.channel = Channel(snippet["channelId"])
        else:
            raise findError

    async def getEmbed(self, author):
        embed = discord.Embed(title = self.title, url = self.url, description = self.description, color = colour)
        embed.set_author(name = self.channel.title, url = self.channel.url, icon_url = self.channel.icon)
        embed.set_thumbnail(url = self.thumbnail)
        embed.add_field(name="Videos", value = self.videos, inline=True)
        embed = Funcs.SetFooter(embed, author, "Playlist")
        return embed

class Channel():

    def __init__(self, id):
        channel = yt.get_channel_info(channel_id = id).to_dict()
        self.url = f"https://www.youtube.com/channel/{id}"

        if channel["pageInfo"]["totalResults"] > 0:
            snippet = channel["items"][0]["snippet"]
            statistics = channel["items"][0]["statistics"]
            self.title = snippet["title"]
            self.description = snippet["description"]
            self.icon = snippet["thumbnails"]["default"]["url"]
            self.subscribers = statistics["subscriberCount"]
            self.videos = statistics["videoCount"]
            self.views = statistics["viewCount"]
        else:
            raise findError

    async def getEmbed(self, author):
            embed = discord.Embed(description = self.description, color = colour)
            embed.set_author(name = self.title, url = self.url, icon_url = self.icon)
            embed.add_field(name = "Subscribers", value = self.subscribers, inline=True)
            embed.add_field(name = "Videos", value = self.videos, inline=True)
            embed.add_field(name = "Total Views", value = self.views, inline=True)
            embed = Funcs.SetFooter(embed, author, "Channel")
            return embed