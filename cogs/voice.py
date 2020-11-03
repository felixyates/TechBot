import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

global vc_is_paused
vc_is_paused = False

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leave(self,ctx):
        "Leave a voice channel"
        await ctx.voice_client.disconnect()
    
    @commands.command(pass_context=True)
    async def fnaf(self,ctx):
        "Plays the FNAF phone call in the voice channel"
        # grab the user who sent the command
        user = ctx.message.author
        channel = user.voice.channel
        if channel!= None:
            # grab user's voice channel
            channelName=channel.name
            await ctx.channel.send('@'+str(user)+' is in channel: '+ channelName)
            # create StreamPlayer
            global vc
            vc= await channel.connect()
            vc.play(discord.FFmpegPCMAudio('fnaf.mp3'), after=lambda e: print('done', e))
            while vc.is_playing() == True:
                await asyncio.sleep(1)
            # disconnect after the player has finished
            vc.stop()
            await self.leave(ctx)
        else:
            await ctx.channel.send("Join a channel first.")
            await ctx.channel.send(user).format(ctx.message.author.mention())

    @commands.command(pass_context=True)
    async def stop(self,ctx):
        "Stops the currently playing audio in voice chat"
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