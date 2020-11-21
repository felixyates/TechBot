import discord
import os
import asyncio
#import youtube_dl
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout

class Troll(commands.Cog, name="troll"):
    def __init__(self, bot):
        self.bot = bot
        # test acc - 761923390104797194
        # tom gab - 662812073390112846s
        # techlife server - 340043063798005780

    def voiceCum(self,member, before, after):
        # memberID - 330779070159650817
        # guildID - 772057284650074162
        guild = self.bot.get_guild(772057284650074162)
        # member = guild.get_member(414444774523928578)
        if guild.id == 772057284650074162:
            """if member.id == 662812073390112846:
                time.sleep(random.randint(60,300))
                await member.move_to(None)"""
            if member.id == 414444774523928578: #george
                if before.channel is None and after.channel is not None:
                    channel = member.voice.channel
                    if member.voice.channel != None:
                        vc= await channel.connect()
                        path = 'voice/anoos.mp3'
                        vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
                        while vc.is_playing() == True:
                            await asyncio.sleep(1)
                        # Disconnects the bot once the track has played out
                        vc.stop()
                        await vc.disconnect()
            elif member.id == 565343237011800084:
                if before.channel is None and after.channel is not None:
                    channel = member.voice.channel
                    if member.voice.channel != None:
                        vc= await channel.connect()
                        path = 'voice/female.mp3'
                        vc.play(discord.FFmpegPCMAudio(path), after=lambda e: print('done', e))
                        while vc.is_playing() == True:
                            await asyncio.sleep(1)
                        # Disconnects the bot once the track has played out
                        vc.stop()
                        await vc.disconnect()

    @commands.Cog.listener()
    async def disconnectem(self):
        userID = 761923390104797194
        guildID = 340043063798005780
        run = True
        guild = self.bot.get_guild(guildID)
        member = guild.get_member(userID)
        while run == True:
            if member.voicestate.channel != None:
                await member.move_to(None)

def setup(bot):
    bot.add_cog(Troll(bot))