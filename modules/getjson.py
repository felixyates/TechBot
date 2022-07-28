import json
from modules import vars

def getServers():
    "Loads the servers from the `servers.json` file."
    with open(vars.JSONPATH, 'r') as f:
        servers = json.load(f)
        return servers

def updateServers(servers):
    "Updates the `servers.json` file."
    with open(vars.JSONPATH, 'w') as f:
        json.dump(servers, f, indent=4)

def secret(fetch):
    """Fetches a secret from the `secrets.json` file
    e.g. Discord, Spotify, YouTube API keys."""
    with open('secrets.json', "r") as f:
        secrets = json.load(f)
        return secrets[fetch]