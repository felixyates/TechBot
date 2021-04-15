import discord

def setembedvar(colour, title, description="", url="", author="", author_url="", author_icon="", thumbnail=""):

    if colour == "G":
        colour = 0x00ff00
    elif colour == "R":
        colour = 0xff0000

    if url != "":
        embed = discord.Embed(color=colour, title=title, description=description, url=url)
    else:
        embed = discord.Embed(color=colour, title=title, description=description)

    if author != "" and author_url != "" and author_icon != "":
        embed.set_author(name=author, url=author_url, icon_url=author_icon)
    
    if thumbnail != "":
        embed.set_thumbnail(url=thumbnail)

    return embed

def addembedfield(embed, name, value, inline: bool):
    embed.add_field(name=name,value=value,inline=inline)
    return embed

def requestedbyfooter(embed,message):
    embed.set_footer(text=f"Requested by {message.author.display_name}",icon_url=message.author.avatar_url)
    return embed