## Send a YouTube / Spotify URL and TechBot will react with upvote and downvote
## Future versions will delete the original message and send an embed with:
    ## Album art
    ## Track/playlist length
    ## Playlist/song length
    ## Recommended by
    ## Etc.

import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from async_timeout import timeout
from modules.emoji import upvote,downvote

class SongRecommendations(commands.Cog, name="songrecommendations"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,message):
        guild = 804016290972172378 # techsmp
        channel = 825330039884480522 # music
        if (message.guild.id == guild) and (message.channel.id == channel):
            await message.add_reaction(upvote)
            await message.add_reaction(downvote)

def setup(bot):
    bot.add_cog(SongRecommendations(bot))