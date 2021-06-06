import json, discord
from discord.ext import commands
from modules.variables import defaultPrefix

def loadServerJson():

    with open('servers.json', 'r') as f:
        
        servers = json.load(f)

    return servers

def updateServerJson(servers):
    
    with open('servers.json', 'w') as f:

        json.dump(servers, f, indent=4)

def secret(fetch):

    with open("secrets.json", "r") as f:

        secrets = json.load(f)
        return secrets[fetch]

def get_prefix(bot, message):

    try:

        with open("servers.json", "r") as f:

            servers = json.load(f)

        return commands.when_mentioned_or(servers[str(message.guild.id)]["prefix"])(bot, message)
    
    except:

        return commands.when_mentioned_or(defaultPrefix)(bot, message)

def thisServerJson(guildID):

    with open('servers.json', 'r') as f:

        servers = json.load(f)
        server = servers[str(guildID)]
        return server