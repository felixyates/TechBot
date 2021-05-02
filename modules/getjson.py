import json

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