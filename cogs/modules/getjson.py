import json, discord
from discord.ext import commands

path = 'servers.json'

def loadServerJson():
    "Loads the `servers.json` file."
    with open(path, 'r') as f:
        servers = json.load(f)
    return servers

def updateServerJson(servers):
    "Updates the `servers.json` file."
    with open(path, 'w') as f:
        json.dump(servers, f, indent=4)

def thisServerJson(guildID):
    "Loads the specified server's JSON data from the `servers.json` file."
    with open(path, 'r') as f:
        servers = json.load(f)
        server = servers[str(guildID)]
        return server

def secret(fetch):
    """Fetches a secret from the `secrets.json` file
    e.g. Discord, Spotify, YouTube API keys."""
    with open(path, "r") as f:
        secrets = json.load(f)
        return secrets[fetch]

def get_prefix(bot, message):
    "Loads the bot prefix from the `servers.json` file."
    with open(path, "r") as f:
        servers = json.load(f)
    return commands.when_mentioned_or(servers[str(message.guild.id)]["prefix"])(bot, message)