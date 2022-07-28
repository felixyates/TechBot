import discord, aiosqlite, json
from discord.ext import commands
from modules import getjson, vars

TOKEN = getjson.secret("discord")
intents = discord.Intents().default()
bot = commands.Bot(intents = intents)

async def db_check():
    "Checks if the database is configured"
    async with aiosqlite.connect(vars.DBPATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS servers(
            "guild_id"	TEXT NOT NULL UNIQUE,
            "name"	INTEGER NOT NULL,
            "owner_id"	TEXT NOT NULL,
            PRIMARY KEY("guild_id")
        )''') # creates servers table
        await db.execute('''CREATE TABLE IF NOT EXISTS welcome(
            "guild_id"	TEXT NOT NULL UNIQUE,
            "state"	INTEGER NOT NULL DEFAULT 0,
            "channel_id"	TEXT,
            "message"	TEXT,
            PRIMARY KEY("guild_id"),
            FOREIGN KEY("guild_id") REFERENCES "servers"("guild_id") ON DELETE CASCADE
        )''') # creates welcome table
        await db.execute('''CREATE TABLE IF NOT EXISTS slurdetector(
            "guild_id"	TEXT NOT NULL UNIQUE,
            "state"	INTEGER NOT NULL DEFAULT 0,
            "channel_id"	TEXT,
            PRIMARY KEY("guild_id"),
            FOREIGN KEY("guild_id") REFERENCES "servers"("guild_id") ON DELETE CASCADE
        )''') # creates slurdetector table
        await db.execute('''CREATE TABLE IF NOT EXISTS slurdetector_cases(
	        "guild_id"	TEXT NOT NULL,
	        "author_id"	TEXT NOT NULL,
            "message_content"	TEXT NOT NULL,
            "message_channel"	TEXT NOT NULL,
            "detected"	TEXT NOT NULL,
	        FOREIGN KEY("guild_id") REFERENCES "servers"("guild_id") ON DELETE CASCADE
        )''') # creates slurdetector_cases table
        await db.execute('''CREATE TABLE IF NOT EXISTS music(
            "guild_id"	TEXT NOT NULL UNIQUE,
            "state"	INTEGER NOT NULL DEFAULT 0,
            "channel_id"	TEXT,
            FOREIGN KEY("guild_id") REFERENCES "servers"("guild_id") ON DELETE CASCADE,
            PRIMARY KEY("guild_id")
        )''') # creates music table
        await db.execute('''CREATE TABLE IF NOT EXISTS textresponder(
            "guild_id"	TEXT NOT NULL UNIQUE,
            "state"	INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY("guild_id"),
            FOREIGN KEY("guild_id") REFERENCES "servers"("guild_id") ON DELETE CASCADE
        )''') # creates textresponder table
        await db.execute('''CREATE TABLE IF NOT EXISTS textresponder_triggers(
	        "guild_id"	TEXT NOT NULL,
	        "created_by_id"	TEXT NOT NULL,
            "type"	INTEGER NOT NULL,
            "trigger"	TEXT NOT NULL,
            "response"	TEXT NOT NULL,
	        FOREIGN KEY("guild_id") REFERENCES "servers"("guild_id") ON DELETE CASCADE
        )''') # creates textresponder_triggers table
        await db.commit()
        print("Database checked/created successfully")

async def db_import(server_id: str):
    with open(vars.jsonPath, 'r') as f:
        servers = json.load(f)
        server = servers[server_id]

        welcome = server["welcome"]
        slurdetector = server["slurdetector"]
        music = server["music"]
        textresponder = server["textresponder"]
        triggers = textresponder["triggers"]
        owner = server["owner"]

        async with aiosqlite.connect(vars.dbPath) as db:
            await db.execute("INSERT INTO servers VALUES(?, ?, ?)", (server_id, server["name"], owner["id"]))
            await db.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, welcome["enabled"], welcome["channel"], welcome["message"]))
            await db.execute("INSERT INTO slurdetector VALUES(?, ?, ?)", (server_id, slurdetector["enabled"], slurdetector["channel"]))
            await db.execute("INSERT INTO music VALUES(?, ?, ?)", (server_id, music["enabled"], music["channel"]))
            await db.execute("INSERT INTO textresponder VALUES(?, ?)", (server_id, textresponder["enabled"]))
            for trigger in triggers:
                responder = triggers[trigger]
                await db.execute("INSERT INTO textresponder_triggers VALUES(?, ?, ?, ?, ?)", (server_id, responder["added_by"], responder["type"], trigger, responder["response"]))
            await db.commit()
        
        print(f"Added server {server_id} (friendly name: {server['name']}) to the database")

async def db_migrate():
    """Migrates the JSON database to the SQLite database.
        - This is a one-time process, and should only be run once."""
    with open(vars.jsonPath, 'r') as f:
        servers = json.load(f)
        for server_id in servers:
            await db_import(server_id)
        print("Migration complete. Please check database before use, and change migrateJSON to False in variables.py.")
        print("You should be able to safely delete the servers.json file, but it is recommended to keep it for backup.")

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user.name} / {bot.user.id}"+"\n------")
    print("Database checks commencing...")
    await db_check()
    print("Database checks completed successfully")
    shouldImport = input("Would you like to import past data from the servers.json file? (y/n) ")
    if shouldImport == "y":
        await db_migrate()

bot.run(TOKEN)