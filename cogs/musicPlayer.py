import discord, asyncio, youtube_dl
from discord.ext import commands
from discord_slash import cog_ext

y = "✅"
n = "❌"
play = "▶"
pause = "⏸"

async def join(self, ctx):

    if ctx.author.voice is None:
        await ctx.send(f"{n} Join a voice channel first")
    else:
        voice_channel = ctx.author.voice.channel
    
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send(f"{y} Joined {voice_channel.mention}")
        else:
            await ctx.voice_client.move_to(voice_channel)

async def leave(self, ctx):

    await ctx.voice_client.disconnect()
    await ctx.send(f"{y} Left voice channel")

async def pause(self, ctx):

    await ctx.voice_client.pause()
    await ctx.send(f"{pause} Paused")

async def resume(self, ctx):

    await ctx.voice_client.resume()
    await ctx.send(f"{play} Resumed")

async def play(self, ctx, url):
    
    ctx.voice_client.stop()
    FFMPEG_OPTIONS = {"before_options":"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options":"-vn"}
    YDL_OPTIONS = {"format":"bestaudio"}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        vc.play(source)

class MusicPlayer(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name = "join")
    async def regular_join(self, ctx):
        
        await join(self, ctx)

    @commands.command(name = "leave")
    async def regular_leave(self, ctx):
        
        await leave(self, ctx)

    @commands.command(name = "pause")
    async def regular_pause(self, ctx):
        
        await pause(self, ctx)

    @commands.command(name = "resume")
    async def regular_resume(self, ctx):
        
        await resume(self, ctx)

    @commands.command(name = "play")
    async def regular_play(self, ctx, url):
        
        await play(self, ctx, url)


def setup(bot:commands.Bot):
    bot.add_cog(MusicPlayer(bot))