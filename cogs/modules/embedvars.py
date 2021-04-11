import discord

def setembedvar(colour,title,value,inline: bool):
    if colour == "G":
        colour = 0x00ff00
    elif colour == "R":
        colour = 0xff0000
    embedVar = discord.Embed(color=colour)
    embedVar.add_field(name=title,value=value,inline=inline)
    return embedVar