BOTNAME = botName = 'TechBot'
    # This is the bot's default name
STATUSCHANNEL = statusChannel = 886048985645715486
    # The bot sends status messages here - e.g. when it is offline / in maintenance mode
DMCHANNEL = dmChannel = 886049452614377492
    # The bot forwards its direct messages here (except for those from other bots)
BOTSERVERSCHANNEL = botServersChannel = 886049432934703164
    # The channel in which bot add/remove events are logged
ERRORCHANNEL = errorChannel = 886049364785643541
    # The channel in which errors that occur are logged
DBPATH = dbPath = 'database.sqlite3'
    # The path to the bot database, used for storing server settings and user info
JSONPATH = jsonPath = "servers.json"
    # The path to the bot's servers.json file.
    # *This is no longer used, it is only for migration to the new database system.*
MIGRATEJSON = migrateJSON = False
    # If True, the bot will migrate the servers.json file to the database upon ready
OWNERGUILDS = [886048985205334066]
    # List of guild ids in which the bot's management commands are available.
    # This does *not* make commands available to non-owners, only makes them visible in these guilds

# Configure embeds in embs.py

# Owner.py
STREAMINGURL = streamingURL = 'https://www.twitch.tv/techlifeyt' # used when the bot's status is set to 'streaming'