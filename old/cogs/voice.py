import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

global vc_is_paused
vc_is_paused = False

# Checks and stores currently available mp3 files
global available
available = []
availableFile = open("voice/available.txt")
available = availableFile.read().splitlines()
availableFile.close()

class Voice(commands.Cog, name="voice"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def leave(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.Cog.listener()
    async def player(self,ctx,path,mode):
        global vc
        if mode == 'play':
            user = ctx.message.author
            channel = user.voice.channel
            if channel!= None:
                channelName=channel.name
                # Connects to the voice channel
                vc= await channel.connect()
                # Sends successful join message
                embedVar = discord.Embed(color=0x00ff00)
                embedVar.add_field(name="Joining",value="✅ Joining channel "+ channelName, inline=False)
                await ctx.message.channel.send(embed=embedVar)
                # Creates the FFmpeg player and plays file from path
                vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
                # Allows the volume to be changed
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 1.0
                while vc.is_playing() == True:
                    await asyncio.sleep(1)
                # Disconnects the bot once the track has played out
                vc.stop()
                await self.leave(ctx)
            else:
                # Sends unsuccessful join message
                embedVar = discord.Embed(color=0xff0000)
                embedVar.add_field(name="Couldn't play",value="❎ Join a voice channel first.", inline=False)
                await ctx.message.channel.send(embed=embedVar)
        elif mode == 'volume':
            if vc!=None:
                message = ctx.message.content
                message = message.split(" ")
                msgvolume = float(message[1])
                volume = float(message[1])/100
                if (msgvolume >= 0) and (msgvolume <= 100):
                    if vc.is_playing() == True:
                        print("\nVoice connection is active\n")
                        vc.source.volume = volume
                        print("Successfully changed volume")
                        # Sends successful volume change
                        embedVar = discord.Embed(color=0x00ff00)
                        embedVar.add_field(name="Volume changed",value="✅ Set volume to "+ str(msgvolume)+ "%", inline=False)
                        await ctx.message.channel.send(embed=embedVar)
                    else:
                        # Sends unsuccessful volume change as nothing is playing
                        embedVar = discord.Embed(color=0xff0000)
                        embedVar.set_footer(text="Volume value was correct, though.")
                        embedVar.add_field(name="Volume not changed",value="❎ Nothing is playing!", inline=False)
                        await ctx.message.channel.send(embed=embedVar)
            else:
                embedVar = discord.Embed(color=0xff0000)
                embedVar.add_field(name="Volume not changed",value="❎ Nothing is playing!", inline=False)
                await ctx.message.channel.send(embed=embedVar)
        elif mode == 'loop':
            print('loop')
        elif mode == 'pause':
            print('pause')
        elif mode == 'resume':
            print('resume')

    @commands.command(pass_context=True)
    async def volume(self,ctx):
        "Sets the volume of the bot"
        await self.player(ctx,'','volume')

    @commands.command(pass_context=True)
    async def stop(self,ctx):
        "Stops the currently playing audio in voice chat."
        if vc.is_playing() == True:
            vc.stop()
            await self.leave(ctx)
            vc_is_paused == False
            embedVar = discord.Embed(color=0x00ff00)
            embedVar.add_field(name="Stopped",value="✅ Stopped playing sound", inline=False)
            await ctx.message.channel.send(embed=embedVar)
        else:
            embedVar = discord.Embed(color=0xff0000)
            embedVar.add_field(name="Didn't stop",value="❎ Nothing is playing!", inline=False)
            await ctx.message.channel.send(embed=embedVar)
    
    @commands.command(pass_context=True)
    async def play(self,ctx):
        "Plays the specified mp3 file"
        message = ctx.message.content.split(" ")
        print(message)
        found = False
        i = 0
        for i in range(len(available)):
            print(available[i])
            if message[1] == available[i]:
                path = 'voice/'+message[1]+'.mp3'
                found = True
                print("Found",path)
                await self.player(ctx,path,'play')
            i += 1

        if found != True:
            embedVar = discord.Embed(color=0xff0000)
            embedVar.add_field(name="Didn't play",value="❎ "+ message[1]+ " is not a valid filename. Use >help to see available audio files.", inline=False)
            await ctx.message.channel.send(embed=embedVar)

"""
    @commands.command(pass_context=True)
    async def pause(self,ctx):
        "Pauses the currently playing audio in voice chat"
        await self.player(ctx,'','pause')

    @commands.command(pass_context=True)
    async def resume(self,ctx):
        "Resumes the currently playing audio in voice chat"
        await self.player(ctx,'','resume') """

def setup(bot):
    bot.add_cog(Voice(bot))