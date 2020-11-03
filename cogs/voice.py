import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

global vc_is_paused
vc_is_paused = False

class Voice(commands.Cog, name="voice"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def leave(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.Cog.listener()
    async def player(self,ctx,path):
        user = ctx.message.author
        channel = user.voice.channel
        if channel!= None:
            # grab user's voice channel
            channelName=channel.name
            await ctx.channel.send('User'+ ' is in channel: '+ channelName)
            # create StreamPlayer
            global vc
            vc= await channel.connect()
            vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
            while vc.is_playing() == True:
                await asyncio.sleep(1)
            # disconnect after the player has finished
            vc.stop()
            await self.leave(ctx)
        else:
            await ctx.channel.send("Join a channel first.")
    
    @commands.command(pass_context=True)
    async def fnaf(self,ctx):
        "Plays the FNAF phone call in the voice channel"
        path = 'fnaf.mp3'
        await self.player(ctx,path)
    
    @commands.command(pass_context=True)
    async def cats(self,ctx):
        "As per Harry's request. Don't even ask."
        path = 'cats.mp3'
        await self.player(ctx,path)
    
    @commands.command(pass_context=True)
    async def fortnite(self,ctx):
        "Plays the old Fortnite Christmas music in the voice channel"
        path = 'fortnite.mp3'
        await self.player(ctx,path)

    @commands.command(pass_context=True)
    async def boom(self,ctx):
        "Plays the vine boom sound effect in the voice channel"
        path = 'boom.mp3'
        await self.player(ctx,path)

    @commands.command(pass_context=True)
    async def breakfromads(self,ctx):
        "Plays the Spotify 'Wanna break from the ads?' clip in the voice channel"
        path = 'breakfromads.mp3'
        await self.player(ctx,path)

    @commands.command(pass_context=True)
    async def bruh(self,ctx):
        "Plays the bruh sound effect in the voice channel"
        path = 'bruh.mp3'
        await self.player(ctx,path)

    @commands.command(pass_context=True)
    async def wifi(self,ctx):
        "Plays the 'Get WiFi anywhere you go' clip in the voice channel"
        path = 'wifi.mp3'
        await self.player(ctx,path)

    @commands.command(pass_context=True)
    async def stop(self,ctx):
        "Stops the currently playing audio in voice chat."
        if vc.is_playing() == True:
            vc.stop()
            await self.leave(ctx)
            vc_is_paused == False
            await ctx.channel.send("Stopped!")
        else:
            await ctx.channel.send("Nothing is playing!")

def setup(bot):
    bot.add_cog(Voice(bot))
        
# @commands.command(pass_context=True)
# async def pause(ctx):
#     "Pauses the currently playing audio in voice chat"
#     if vc.is_playing() == True:
#         vc.pause()
#         await ctx.channel.send("Paused!")
#         global vc_is_paused
#         vc_is_paused = True
#     else:
#         await ctx.channel.send("Nothing is playing!")

# @commands.command(pass_context=True)
# async def resume(ctx):
#     "Resumes the currently playing audio in voice chat"
#     if vc_is_paused == True:
#         vc.resume()
#         while vc.is_playing() != True:
#             await asyncio.sleep(1)
#         await ctx.channel.send("Resumed!")
#     else:
#         await ctx.channel.send("Nothing is playing!")