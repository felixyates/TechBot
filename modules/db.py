import aiosqlite, json, discord
from modules import vars, embs, srv

async def load(guild_id: str):
    async with aiosqlite.connect(vars.DBPATH) as db:
        async with db.execute("SELECT * FROM servers WHERE id = ?", (guild_id,)) as cursor:
            return await cursor.fetchone()

async def loadServers(bot: discord.Bot) -> "list[srv.Server]":
    servers = []
    async for guild in bot.fetch_guilds():
        server = srv.Server(guild)
        await server.GetModules()
        servers.append(server)
    return servers

async def modify(query: str, parameters: tuple):
    async with aiosqlite.connect(vars.DBPATH) as db:
        await db.execute(query, parameters)
        await db.commit()

async def modify(query: str, parameters: tuple):
    async with aiosqlite.connect(vars.DBPATH) as db:
        await db.execute_insert(query, parameters)
        await db.commit()

async def execute(query: str, parameters: tuple):
    async with aiosqlite.connect(vars.DBPATH) as db:
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchall()

async def RemoveResponder(guild_id: str, trigger: str):
    await modify(f'''DELETE * FROM textresponder_triggers WHERE trigger = {trigger} AND guild_id = {guild_id}''')

async def AddResponder(guild_id: str, created_by_id: str, type: int, trigger: str, response: str):
    await modify(f"INSERT INTO textresponder_triggers VALUES(?,?,?,?,?)", (guild_id, created_by_id, type, trigger, response))

async def rowProcessor(row: aiosqlite.Row, description: tuple) -> dict:
    dict = {}
    for i in range(len(row)):
        dict[description[i][0]] = row[i]
    return dict

async def loadModule(guild_id: str, module: str):
    async with aiosqlite.connect(vars.dbPath) as db:
        async with db.execute(f"""SELECT * FROM {module} WHERE guild_id = ?""", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            description = cursor.description
            return await rowProcessor(row, description)

async def updateModule(guild_id: str, module: str, attribute: str, value):
    try:
        await modify(f"UPDATE {module} SET {attribute} = ? WHERE guild_id = ?", (value, guild_id))
        return {
            'successful': True,
            'embed': embs.Success("Successfully updated module")
        }
    except Exception as e:
        return {
            'successful': False,
            'embed': embs.Failure("Couldn't update module. Try again, or contact support.", e)
        }