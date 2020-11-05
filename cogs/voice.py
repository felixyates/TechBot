import discord
import os
import asyncio
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
    async def player(self,ctx,path,mode):
        global vc
        if mode == 'play':
            user = ctx.message.author
            channel = user.voice.channel
            if channel!= None:
                channelName=channel.name
                # Sends successful join message
                embedVar = discord.Embed(color=0x00ff00)
                embedVar.add_field(name="Joining",value="✅ Joining channel "+ channelName, inline=False)
                await ctx.message.channel.send(embed=embedVar)
                # Connects to the voice channel
                vc= await channel.connect()
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
    async def fnaf(self,ctx):
        "Plays the FNAF phone call in the voice channel"
        path = 'voice/fnaf.mp3'
        await self.player(ctx,path,'play')
    
    @commands.command(pass_context=True)
    async def fortnite(self,ctx):
        "Plays the old Fortnite Christmas music in the voice channel"
        path = 'voice/fortnite.mp3'
        await self.player(ctx,path,'play')

    @commands.command(pass_context=True)
    async def boom(self,ctx):
        "Plays the vine boom sound effect in the voice channel"
        path = 'voice/boom.mp3'
        await self.player(ctx,path,'play')

    @commands.command(pass_context=True)
    async def breakfromads(self,ctx):
        "Plays the Spotify 'Wanna break from the ads?' clip in the voice channel"
        path = 'voice/breakfromads.mp3'
        await self.player(ctx,path,'play')

    @commands.command(pass_context=True)
    async def bruh(self,ctx):
        "Plays the bruh sound effect in the voice channel"
        path = 'voice/bruh.mp3'
        await self.player(ctx,path,'play')

    @commands.command(pass_context=True)
    async def wifi(self,ctx):
        "Plays the 'Get WiFi anywhere you go' clip in the voice channel"
        path = 'voice/wifi.mp3'
        await self.player(ctx,path,'play')

    @commands.command(pass_context=True)
    async def beyondthesea(self,ctx):
        "Plays Beyond the Sea by Bobby Darin in the voice channel"
        path = 'voice/beyondthesea.mp3'
        await self.player(ctx,path,'play')

    @commands.command(pass_context=True)
    async def minecraftAlpha(self,ctx):
        "Plays 'Minecraft: Volume Alpha' in the voice channel"
        path = 'voice/minecraftAlpha.mp3'
        await self.player(ctx,path,'play')

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
    
"""     @commands.command(pass_context=True)
    async def pause(self,ctx):
        "Pauses the currently playing audio in voice chat"
        await self.player(ctx,'','pause')

    @commands.command(pass_context=True)
    async def resume(self,ctx):
        "Resumes the currently playing audio in voice chat"
        await self.player(ctx,'','resume') """

def setup(bot):
    bot.add_cog(Voice(bot))