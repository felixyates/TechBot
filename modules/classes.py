import discord, aiosqlite
from modules import db, vars

class Responder:

    def __init__(self, guild_id, trigger: str, **kwargs):
        self.guild_id = str(guild_id)
        self.trigger = trigger
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    async def DoesExist(self):
        async with aiosqlite.connect(vars.dbPath) as db:
            async with db.execute("SELECT * FROM textresponder_triggers WHERE guild_id = ? AND trigger = ?", (self.guild_id, self.trigger)) as cursor:
                row = await cursor.fetchone()
                return row
    
    async def Add(self):
        try:
            if not (self.DoesExist()[0]):
                await db.AddResponder(self.guild_id, self.created_by_id, self.type, self.trigger, self.response)
                return True
        except Exception as e:
            return False, e
    
    async def Remove(self):
        try:
            if (await self.DoesExist()[0]):
                await db.RemoveResponder(self.guild_id, self.trigger)
                return True
        except Exception as e:
            return False, e

    async def ShouldSend(self, message: str) -> bool:
        if self.type == 1:
            if self.trigger == message.content:
                return True
        elif self.type == 2:
            if self.trigger in message.content:
                return True
        elif self.type == 3:
            if self.trigger.upper() == message.content.upper():
                return True
        elif self.type == 4:
            if self.trigger.upper() in message.content.upper():
                return True
        return False
