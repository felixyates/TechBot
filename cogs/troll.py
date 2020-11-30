from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
import discord, os, asyncio, random, sys
import smtplib, ssl, utils
import subprocess, time
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import CommandNotFound, CommandInvokeError
from async_timeout import timeout

class Troll(commands.Cog, name="troll"):
    def __init__(self, bot):
        self.bot = bot
        # test acc - 761923390104797194
        # tom gab - 662812073390112846s
        # techlife server - 340043063798005780

    @commands.Cog.listener()
    def on_voice_state_update(self,member, before, after):
        guild = self.bot.get_guild(772057284650074162)
        if guild.id == 772057284650074162:
            if member.id == 414444774523928578: # george
                if before.channel is None and after.channel is not None:
                    channel = member.voice.channel
                    if member.voice.channel != None:
                        voicechannel = await channel.connect()
                        path = 'voice/anoos.mp3'
                        voicechannel.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
                        while voicechannel.is_playing() == True:
                            await asyncio.sleep(1)
                        # Disconnects the bot once the track has played out
                        voicechannel.stop()
                        await voicechannel.disconnect()
            elif member.id == 565343237011800084:
                if before.channel is None and after.channel is not None:
                    channel = member.voice.channel
                    if member.voice.channel != None:
                        voicechannel = channel.connect()
                        path = 'voice/female.mp3'
                        voicechannel.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
                        while voicechannel.is_playing() == True:
                            await asyncio.sleep(1)
                        # Disconnects the bot once the track has played out
                        voicechannel.stop()
                        await voicechannel.disconnect()

"""     @commands.Cog.listener()
    async def disconnectem(self):
        userID = 761923390104797194
        guildID = 340043063798005780
        run = True
        guild = self.bot.get_guild(guildID)
        member = guild.get_member(userID)
        while run == True:
            if member.voicestate.channel != None:
                await member.move_to(None) """

## this went in on_voice_state_update
"""if member.id == 662812073390112846:
                time.sleep(random.randint(60,300))
                await member.move_to(None)""" # this auto-kicks tom gab from vc every 1 - 5 minutes he's in a vc

def setup(bot):
    bot.add_cog(Troll(bot))